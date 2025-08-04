import time
from predict import main, should_predict, create_predictions_table_if_needed

WAIT_SECONDS = 30  # vérifie toutes les 30 secondes

if __name__ == "__main__":
    print("Démarrage du service de prédiction synchronisé...")
    
    # créer la table si elle n'existe pas
    create_predictions_table_if_needed()
    
    while True:
        if should_predict():
            print("Nouvelle bougie détectée. Prédiction en cours...")
            main()
        else:
            print("En attente d'une nouvelle bougie OHLCV...")
        time.sleep(WAIT_SECONDS)
