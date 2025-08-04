import pandas as pd
import numpy as np
import psycopg2
import joblib
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime

# -----------------------------
# Paramètres
SEQ_LEN = 12  # 1 heure d'historique
FEATURES = ['open', 'high', 'low', 'close', 'volume']
MODEL_PATH = "/app/model.pkl"
TABLE_NAME = "binance_ohlcv_5m"

DB_PARAMS = {
    "dbname": "binance_data",
    "user": "VALDML",
    "password": "PROJETOPA", 
    "host": "postgres",
    "port": "5432"
}
# -----------------------------

# Charge toutes les données OHLCV depuis PostgreSQL
def load_data():
    print("Connexion à PostgreSQL...")
    conn = psycopg2.connect(**DB_PARAMS)
    query = f"""
        SELECT timestamp, open, high, low, close, volume
        FROM {TABLE_NAME}
        WHERE symbol = 'BTC/USDT'
        ORDER BY timestamp ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index().dropna()
    return df

# Transforme les données en fenêtres (X) et cibles (y)
def create_dataset(df):
    print("Construction des fenêtres d'entraînement...")
    X, y = [], []
    for i in range(SEQ_LEN, len(df) - 1):
        window = df.iloc[i-SEQ_LEN:i][FEATURES].values.flatten()
        target = df.iloc[i + 1]['close']  # t+1 = dans 5 min
        X.append(window)
        y.append(target)
    X = np.array(X)
    y = np.array(y)
    print(f"Dataset prêt : {X.shape[0]} échantillons, {X.shape[1]} features")
    return X, y

# Entraîne le modèle et le sauvegarde
def train_and_save_model(X, y):
    print("Entraînement du modèle...")
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Utilisation du modèle Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Évaluation simple : R²
    score = model.score(X_test, y_test)
    print(f"Score R² sur le jeu de test : {score:.4f}")

    # Point d’entrée
    joblib.dump(model, MODEL_PATH)
    print(f"Modèle sauvegardé sous {MODEL_PATH}")

def main():
    df = load_data()
    X, y = create_dataset(df)
    train_and_save_model(X, y)

if __name__ == "__main__":
    main()
