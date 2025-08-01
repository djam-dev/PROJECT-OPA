import psycopg2
import os
import pandas as pd
from datetime import datetime, timedelta

# Paramètres de connexion
DB_NAME = os.getenv("POSTGRES_DB", "binance_data")
DB_USER = os.getenv("POSTGRES_USER", "VALDML")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "PROJETOPA")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Connexion
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Création des tables si elles n'existent pas
cur.execute("""
CREATE TABLE IF NOT EXISTS aggregated_trades (
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

# Récupération du dernier timestamp
cur.execute("SELECT last_aggregated FROM aggregation_state ORDER BY id DESC LIMIT 1")
last_aggregated = cur.fetchone()
start_time = last_aggregated[0] if last_aggregated else None

# Début d’agrégation
query = """
SELECT symbol, price, quantity, timestamp
FROM binance_trades
{where_clause}
ORDER BY timestamp
"""
where_clause = f"WHERE timestamp > '{start_time}'" if start_time else ""
cur.execute(query.format(where_clause=where_clause))
rows = cur.fetchall()

if not rows:
    print("Aucune nouvelle donnée à agréger.")
    exit()

# Agrégation
df = pd.DataFrame(rows, columns=["symbol", "price", "quantity", "timestamp"])
df["timestamp"] = pd.to_datetime(df["timestamp"])
df.set_index("timestamp", inplace=True)

# On suppose un seul symbole
symbol = df["symbol"].iloc[0]

# Grouper par tranche de 5 min
agg = df.resample("5min").agg({
    "price": ["first", "max", "min", "last"],
    "quantity": "sum"
}).dropna()

agg.columns = ["open", "high", "low", "close", "volume"]
agg["symbol"] = symbol
agg = agg.reset_index().rename(columns={"timestamp": "interval_start"})

# Insertion en base
for _, row in agg.iterrows():
    cur.execute("""
        INSERT INTO aggregated_trades (interval_start, symbol, open, high, low, close, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (interval_start) DO NOTHING
    """, (
        row["interval_start"], row["symbol"], row["open"],
        row["high"], row["low"], row["close"], row["volume"]
    ))

# Mise à jour du dernier timestamp traité
last_timestamp = agg["interval_start"].max()
cur.execute("INSERT INTO aggregation_state (last_aggregated) VALUES (%s)", (last_timestamp,))
conn.commit()
print(f"Agrégation terminée jusqu’à : {last_timestamp}")
