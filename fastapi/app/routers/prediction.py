from fastapi import APIRouter, HTTPException
from app.models.prediction import PredictionOut         # Modèle de sortie (Pydantic) pour la réponse JSON
from app.db.connection import get_db_connection         # Fonction pour obtenir une connexion PostgreSQL

# Création d’un router FastAPI spécifique aux prédictions
router = APIRouter()

@router.get("/last", response_model=PredictionOut)
def get_latest_prediction():
    """
    Endpoint GET /prediction/latest
    Récupère la prédiction la plus récente enregistrée dans la base de données.
    Retourne un objet JSON contenant la date de la prédiction et la valeur prédite.
    """

    # Connexion à la base PostgreSQL
    conn = get_db_connection()

    # Exécution de la requête SQL pour obtenir la dernière prédiction
    with conn.cursor() as cur:
        cur.execute("""
            SELECT prediction_time, predicted_close
            FROM predictions_5m
            ORDER BY prediction_time DESC
            LIMIT 1;
        """)
        row = cur.fetchone()  # Récupère le résultat

    # Fermeture de la connexion
    conn.close()

    # Si aucune ligne n'est retournée, on renvoie une erreur 404
    if not row:
        raise HTTPException(status_code=404, detail="Aucune prédiction trouvée.")

    # On retourne un objet conforme au schéma Pydantic PredictionOut
    return PredictionOut(
        prediction_time=row[0],
        predicted_close=row[1]
    )
