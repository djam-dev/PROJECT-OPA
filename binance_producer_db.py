import websocket
import json
import time
import datetime
import psycopg2
import csv
from pathlib import Path
# Connexion à la base PostgreSQL
last_saved_time = 0  # Dernier moment où on a écrit dans le CSV
save_interval = 1   # Intervalle en secondes entre deux sauvegardes
today = datetime.datetime.now().strftime("%Y-%m-%d")
csv_path = Path(f"binance_trades_{today}.csv")

# Créer le fichier CSV avec en-tête s'il n'existe pas
if not csv_path.exists():
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['symbol', 'price', 'quantity', 'timestamp'])


conn = psycopg2.connect(
    dbname="binance_data",
    user="postgres",
    password="Masri71854415",  # Remplace ici
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def insert_trade(data):
    try:
        timestamp = int(data["T"]) / 1000
        formatted_time = datetime.datetime.fromtimestamp(timestamp)
        query = """
            INSERT INTO binance_trades (symbol, price, quantity, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        values = (data["s"], data["p"], data["q"], formatted_time)
        cur.execute(query, values)
        conn.commit()
        print(f"✅ Inséré : {data['s']} à {formatted_time}")
    except Exception as e:
        print(f"❌ Erreur insertion : {e}")
     
    global last_saved_time
    current_time = time.time()
    if current_time - last_saved_time >= save_interval:
        with open(csv_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([data["s"], data["p"], data["q"], formatted_time])
        last_saved_time = current_time

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "T" in data:
            insert_trade(data)
    except Exception as e:
        print(f"❌ Erreur dans on_message : {e}")

def on_error(ws, error):
    print(f"❌ Erreur WebSocket : {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 Fermeture : {close_status_code}, {close_msg}")
    conn.close()

def on_open(ws):
    print("🔗 Connexion WebSocket établie")
    payload = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade"],
        "id": int(time.time())
    }
    ws.send(json.dumps(payload))

if __name__ == "__main__":
    socket = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    ws = websocket.WebSocketApp(
        socket,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )

    print("🚀 Lancement de la collecte en temps réel...")
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("⏹️ Arrêt manuel")
        ws.close()
        conn.close()
