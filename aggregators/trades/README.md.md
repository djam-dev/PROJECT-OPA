# Aggregator - Binance Trade Aggregation

Ce service est un agrégateur de données de trade en provenance de la base PostgreSQL `binance_data`.  
Il a pour objectif de regrouper les trades par intervalles de 5 minutes (ou autre fréquence définie) afin de :

- Réduire le volume de données à traiter côté Machine Learning
- Faciliter la visualisation et les statistiques
- Permettre des prédictions sur des buckets temporels homogènes

## 🔧 Fonctionnalités

- Agrégation des trades en intervalles de temps (ex : 5 min)
- Création automatique de la table d’agrégation si elle n’existe pas
- Suivi du dernier `timestamp` agrégé via une table dédiée
- Redémarrage intelligent (ne relance pas toute l'agrégation depuis le début)
- Résilience face à des interruptions de service

## 🛠️ Lancement

```bash
docker compose run --rm aggregator
