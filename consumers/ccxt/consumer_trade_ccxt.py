import psycopg2
import json
import time
import datetime
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import os

# Chargement de la configuration depuis les variables d'environnement
POSTGRES_DB = os.environ.get("POSTGRES_DB", "binance_data")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_SERVER", "kafka:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "Binance_trades")

# Connexion à PostgreSQL avec gestion d'attente
def wait_for_postgres():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT
            )
            print("Connexion PostgreSQL établie.")
            return conn
        except psycopg2.OperationalError as e:
            print(f"⏳ PostgreSQL non disponible... tentative {i+1}/10")
            time.sleep(5)
    raise Exception("Impossible de se connecter à PostgreSQL après 10 tentatives.")

# Connexion à Kafka avec gestion d'attente
def wait_for_kafka():
    for i in range(10):
        try:
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='binance-consumer-ccxt'
            )
            print("Connexion Kafka réussie.")
            return consumer
        except NoBrokersAvailable:
            print(f"⏳ Kafka non disponible... tentative {i+1}/10")
            time.sleep(5)
    raise Exception("Impossible de se connecter à Kafka après 10 tentatives.")

# Connexions
conn = wait_for_postgres()
cur = conn.cursor()
consumer = wait_for_kafka()

# Création de la table si elle n'existe pas
cur.execute("""
    CREATE TABLE IF NOT EXISTS binance_trades (
        symbol TEXT,
        price FLOAT,
        quantity FLOAT,
        timestamp TIMESTAMP
    )
""")
conn.commit()

print("Consumer CCXT démarré et connecté à Kafka et PostgreSQL")

# Fonction d'insertion
def insert_trade(data):
    try:
        timestamp = int(data["timestamp"]) / 1000
        formatted_time = datetime.datetime.fromtimestamp(timestamp)
        query = """
            INSERT INTO binance_trades (symbol, price, quantity, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        values = (
            data["symbol"],
            float(data["price"]),
            float(data["amount"]),
            formatted_time
        )
        cur.execute(query, values)
        conn.commit()
        print(f"Inséré : {data['symbol']} à {formatted_time}")
    except Exception as e:
        print(f"Erreur insertion : {e}")

# Boucle principale Kafka
for message in consumer:
    data = message.value
    print("Message reçu :", data)
    insert_trade(data)
