import pandas as pd
import numpy as np
import psycopg2
import joblib
from datetime import datetime, timedelta
import time

# --- Config ---
SEQ_LEN = 12
FEATURES = ['open', 'high', 'low', 'close', 'volume']
MODEL_PATH = "model.pkl"
TABLE_NAME = "binance_ohlcv_5m"
PREDICT_TABLE = "predictions_5m"

DB_PARAMS = {
    "dbname": "binance_data",
    "user": "VALDML",
    "password": "PROJETOPA",
    "host": "postgres",
    "port": "5432"
}

# Vérifie si une nouvelle bougie est arrivée en base depuis la dernière prédiction
def should_predict():
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        # dernière bougie OHLCV
        cur.execute(f"SELECT MAX(timestamp) FROM {TABLE_NAME} WHERE symbol = 'BTC/USDT';")
        latest_ohlcv = cur.fetchone()[0]

        # dernière prédiction faite
        cur.execute(f"SELECT MAX(prediction_time) FROM {PREDICT_TABLE};")
        latest_pred = cur.fetchone()[0]

    conn.close()

    # Pas de données en base, impossible de prédire.
    if latest_ohlcv is None:
        return False

    # Jamais de prédiction faite, on prédit.
    if latest_pred is None:
        return True

    # on prédit seulement si nouvelle bougie apparue
    return latest_ohlcv > (latest_pred - timedelta(minutes=5))

# Récupère les 12 dernières bougies (triées), les aplatit pour en faire une entrée ML
def get_latest_window():
    conn = psycopg2.connect(**DB_PARAMS)
    query = f"""
        SELECT timestamp, open, high, low, close, volume
        FROM {TABLE_NAME}
        WHERE symbol = 'BTC/USDT'
        ORDER BY timestamp DESC
        LIMIT {SEQ_LEN}
    """
    df = pd.read_sql(query, conn)
    conn.close()

    df = df.sort_values("timestamp")
    if len(df) < SEQ_LEN:
        raise ValueError("Pas assez de données pour prédire.")

    return df[FEATURES].values.flatten()

# Charge le modèle et effectue une prédiction à partir du vecteur de features
def predict_next_close(X_flattened):
    model = joblib.load(MODEL_PATH)
    prediction = model.predict([X_flattened])
    return float(prediction[0])

# Crée la table de prédictions si elle n'existe pas encore
def create_predictions_table_if_needed():
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {PREDICT_TABLE} (
                prediction_time TIMESTAMP PRIMARY KEY,
                predicted_close FLOAT
            );
        """)
        conn.commit()
    conn.close()

# Insère la prédiction dans la base PostgreSQL si elle n’y est pas encore
def insert_prediction(predicted_value, prediction_time):
    conn = psycopg2.connect(**DB_PARAMS)
    with conn.cursor() as cur:
        cur.execute(f"""
            INSERT INTO {PREDICT_TABLE} (prediction_time, predicted_close)
            VALUES (%s, %s)
            ON CONFLICT (prediction_time) DO NOTHING
        """, (prediction_time, predicted_value))
        conn.commit()
    conn.close()

# Fonction principale : vérifie les conditions, effectue la prédiction, l’insère en base
def main():
    try:
        create_predictions_table_if_needed()
        
        if not should_predict():
            print("Aucune nouvelle bougie. Prédiction non effectuée.")
            return
        
        print("Lecture des données OHLCV...")
        X = get_latest_window()
        prediction = predict_next_close(X)

        now = datetime.utcnow()
        next_ts = now + timedelta(minutes=5)
        print(f"Prediction pour {next_ts} : {prediction:.2f}")

        insert_prediction(prediction, next_ts)
        print("Prediction enregistrée")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
