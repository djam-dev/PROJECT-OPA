from pydantic import BaseModel
from datetime import datetime

# Modèle de réponse pour la prédiction
class PredictionOut(BaseModel):
    prediction_time: datetime
    predicted_close: float