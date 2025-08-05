import streamlit as st
import requests

API_URL = "http://fastapi:8000/api/predictions/last"  # conteneur Docker
# API_URL = "http://localhost:8000/api/predictions/last"  # local

st.title("Dernière Prédiction BTC/USDT")

try:
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    st.success("Prédiction récupérée avec succès")
    st.write(f"Horodatage : `{data['prediction_time']}`")
    st.write(f"Clôture prédite : `{data['predicted_close']}` USD")

except requests.exceptions.RequestException as e:
    st.error(f"Erreur lors de la récupération de la prédiction : {e}")
