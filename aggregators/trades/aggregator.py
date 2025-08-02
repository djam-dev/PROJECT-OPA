import psycopg2
import os
import pandas as pd
import time
from datetime import datetime

# Paramètres de connexion
DB_NAME = os.getenv("POSTGRES_DB", "binance_data")
DB_USER = os.getenv("POSTGRES_USER", "VALDML")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "PROJETOPA")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def wait_for_postgres():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            print("Connexion PostgreSQL établie.")
            return conn
        except psycopg2.OperationalError:
            print(f"PostgreSQL pas encore prêt... tentative {i+1}/10")
            time.sleep(3)
    raise Exception("Impossible de se connecter à PostgreSQL après 10 tentatives.")

def run_aggregation():
    conn = wait_for_postgres()
    cur = conn.cursor()

    # Création des tables si elles n'existent pas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS aggregated_ohlcv (
        interval_start TIMESTAMP PRIMARY KEY,
        symbol TEXT,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume FLOAT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS aggregation_state (
        id SERIAL PRIMARY KEY,
        last_aggregated TIMESTAMP
    )
    """)
    conn.commit()

    while True:
        print("Lancement d’un nouveau cycle d’agrégation...")

        cur.execute("SELECT last_aggregated FROM aggregation_state ORDER BY id DESC LIMIT 1")
        last_aggregated = cur.fetchone()
        start_time = last_aggregated[0] if last_aggregated else None

        where_clause = f"WHERE timestamp > '{start_time}'" if start_time else ""
        query = f"""
        SELECT symbol, open, high, low, close, volume, timestamp
        FROM binance_ohlcv
        {where_clause}
        ORDER BY timestamp
        """
        cur.execute(query)
        rows = cur.fetchall()

        if not rows:
            print("Aucune nouvelle bougie à traiter.")
            time.sleep(30)
            continue

        df = pd.DataFrame(rows, columns=["symbol", "open", "high", "low", "close", "volume", "timestamp"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.drop_duplicates(subset="timestamp")

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO aggregated_ohlcv (interval_start, symbol, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (interval_start) DO NOTHING
            """, (
                row["timestamp"], row["symbol"], row["open"],
                row["high"], row["low"], row["close"], row["volume"]
            ))

        last_timestamp = df["timestamp"].max()
        cur.execute("INSERT INTO aggregation_state (last_aggregated) VALUES (%s)", (last_timestamp,))
        conn.commit()

        print(f"Agrégation terminée jusqu’à : {last_timestamp}")
        print("Attente avant prochain cycle...\n")
        time.sleep(30)

if __name__ == "__main__":
    run_aggregation()
