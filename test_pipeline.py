import requests
import json
import time

print("?? Vérification de l’API FastAPI...")
try:
    r = requests.get("http://localhost:8000/docs")
    assert r.status_code == 200
    print("? FastAPI fonctionne !")
except Exception as e:
    print("? FastAPI ne répond pas :", e)

print("?? Test de prédiction...")
try:
    payload = {"price": 107976.92, "quantity": 0.00881}
    headers = {"Content-Type": "application/json"}
    r = requests.post("http://localhost:8000/predict", headers=headers, json=payload)
    print("? Prédiction reçue :", r.json())
except Exception as e:
    print("? Échec de la prédiction :", e)

print("?? Test de la base de données (PGAdmin)...")
try:
    r = requests.get("http://localhost:5050")
    assert r.status_code == 200
    print("? PGAdmin est actif sur le port 5050")
except Exception as e:
    print("? PGAdmin ne répond pas :", e)

print("?? Test de l’interface Kafka UI...")
try:
    r = requests.get("http://localhost:8080")
    assert r.status_code == 200
    print("? Kafka UI est actif sur le port 8080")
except Exception as e:
    print("? Kafka UI ne répond pas :", e)