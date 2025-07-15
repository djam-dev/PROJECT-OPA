import psycopg2
import json
import time
import datetime
import csv
from pathlib import Path
from kafka import KafkaConsumer

# Connexion à PostgreSQL (⚠️ Adapter au conteneur Docker)
conn = psycopg2.connect(
    dbname="binance_data",
    user="VALDML",
    password="PROJETOPA",
    host="postgre",
    port="5432"  # Port interne Docker
)
cur = conn.cursor()

# Créer la table si elle n'existe pas
cur.execute("""
    CREATE TABLE IF NOT EXISTS binance_trades (
        symbol TEXT,
        price FLOAT,
        quantity FLOAT,
        timestamp TIMESTAMP
    )
""")
conn.commit()

# Préparation fichier CSV
last_saved_time = 0
save_interval = 1
today = datetime.datetime.now().strftime("%Y-%m-%d")
csv_path = Path(f"binance_trades_{today}.csv")

if not csv_path.exists():
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['symbol', 'price', 'quantity', 'timestamp'])

consumer = KafkaConsumer(
    'Binance_trades',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    group_id='binance-consumer'
)

print("🎯 Consumer démarré et connecté à Kafka et PostgreSQL")

def insert_trade(data):
    try:
        timestamp = int(data["T"]) / 1000
        formatted_time = datetime.datetime.fromtimestamp(timestamp)
        query = """
            INSERT INTO binance_trades (symbol, price, quantity, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        values = (data["s"], float(data["p"]), float(data["q"]), formatted_time)
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

# Boucle principale Kafka
for message in consumer:
    data = message.value
    insert_trade(data)
