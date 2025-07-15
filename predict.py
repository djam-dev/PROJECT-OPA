import joblib
import numpy as np

# Charger le modèle
model = joblib.load("model.pkl")

def predict_price(price: float, quantity: float) -> float:
    features = np.array([[price, quantity]])
    prediction = model.predict(features)
    return float(prediction[0])


print(predict_price(107976.92 , 0.00881 ))
