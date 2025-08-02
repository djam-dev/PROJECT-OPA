import ccxt
import time
import json
from kafka import KafkaProducer

# CCXT setup
exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1m'  # Tu peux aussi utiliser '5m', '1h', etc.
limit = 500

# Chargement du dernier timestamp
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

# Kafka setup
kafka_producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Point de départ
since = load_last_timestamp()

print(f"Démarrage à partir de {since} pour {symbol} ({timeframe})")

try:
    while True:
        candles = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)

        if candles:
            for candle in candles:
                data = {
                    "timestamp": candle[0],      # ms
                    "open": candle[1],
                    "high": candle[2],
                    "low": candle[3],
                    "close": candle[4],
                    "volume": candle[5],
                    "symbol": symbol,
                    "timeframe": timeframe
                }
                kafka_producer.send("Binance_ohlcv", value=data)

            print(f"{len(candles)} bougies envoyées à Kafka depuis {since}")
            since = candles[-1][0] + exchange.parse_timeframe(timeframe) * 1000  # passe à la bougie suivante
            save_last_timestamp(since)
            time.sleep(exchange.rateLimit / 1000)
        else:
            print("Aucune nouvelle bougie, attente...")
            time.sleep(5)

except KeyboardInterrupt:
    print("Arrêt manuel du producer")
