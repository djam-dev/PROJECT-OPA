# PROJECT-OPA

PROJECT-OPA est une application complète de traitement des données de trading en temps réel provenant de Binance. Elle combine la collecte, le stockage, la modélisation et l'inférence temps réel de données financières à l'aide d'outils modernes tels que Python, PostgreSQL, FastAPI et Docker.

## 📌 Objectifs

- Collecter les données de transactions (trades) de Binance en temps réel.
- Les stocker dans une base de données PostgreSQL.
- Appliquer un modèle de Machine Learning pour effectuer des prédictions sur ces données.
- Fournir une API REST pour interroger les prédictions en temps réel.
- Dockeriser l’ensemble du projet pour un déploiement facile.

---

## 🧱 Structure du projet

```bash
PROJECT-OPA/
│
├── binance_model.ipynb         # Notebook d'entraînement du modèle ML
├── binance_producer_db.py      # Script de collecte et d'insertion dans PostgreSQL
├── main.py                     # Entrée principale de l’API FastAPI
├── predict.py                  # Fonction de prédiction à partir du modèle
├── model.pkl                   # Modèle ML pré-entraîné (pickle)
├── test_db_conn.py             # Test de connexion à la base PostgreSQL
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
└── binance_trades_DATE.csv     # Données brutes sauvegardées localement
