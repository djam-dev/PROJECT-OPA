from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import prediction  # Import du routeur de prédiction

app = FastAPI(
    title="Crypto Price Prediction API",
    description="API pour interroger les prédictions de clôture de BTC/USDT (5min)",
    version="1.0.0",
)

# Middleware CORS (si besoin d'appeler l'API depuis un frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre si besoin en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(prediction.router, prefix="/api/predictions", tags=["Predictions"])


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API de prédiction crypto"}
