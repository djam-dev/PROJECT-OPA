import websocket
import json
import time 
from kafka import KafkaProducer

Kafka_producer = KafkaProducer(
    bootstrap_servers='kafka:9092',  # utilise l'adresse du conteneur kafka dans Docker
    value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def on_message(ws, message):
    try:
        data = json.loads(message)
        if "T" in data:
            Kafka_producer.send('Binance_trades', value=data) #Envoi d'un message au topic Binance_trades
    except Exception as e:
        print(f"❌ Erreur dans on_message : {e}")

def on_error(ws, error):
    print(f"❌ Erreur WebSocket : {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 Fermeture : {close_status_code}, {close_msg}")
    ws.close()

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

