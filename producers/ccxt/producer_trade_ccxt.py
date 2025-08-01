import ccxt
import time
import json
from kafka import KafkaProducer

# CCXT
exchange = ccxt.binance()
symbol = 'BTC/USDT'
limit = 500

def load_last_timestamp(filename="last_timestamp.txt"):
    try:
        with open(filename, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        print("Aucun fichier de timestamp trouvé. Démarrage à partir de 2024-08-01")
        return exchange.parse8601("2024-08-01T00:00:00Z")

def save_last_timestamp(ts, filename="last_timestamp.txt"):
    with open(filename, "w") as f:
        f.write(str(ts))

# Kafka
kafka_producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Chargement de la dernière position
since = exchange.parse8601("2024-08-01T00:00:00Z")

print(f"Démarrage à partir de {since}")

try:
    while True:
        trades = exchange.fetch_trades(symbol, since=since, limit=limit)

        if trades:
            for trade in trades:
                kafka_producer.send('Binance_trades', value=trade)

            print(f"{len(trades)} trades envoyés à Kafka depuis {since}")

            since = trades[-1]['timestamp'] + 1
            save_last_timestamp(since)

            time.sleep(exchange.rateLimit / 1000)
        else:
            print("Aucun nouveau trade, on attend...")
            time.sleep(5)

except KeyboardInterrupt:
    print("Arrêt manuel")
