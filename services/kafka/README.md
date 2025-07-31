# Kafka Service

Ce dossier est réservé à la gestion du service Kafka, orchestré via Docker Compose.

## Image utilisée
- `wurstmeister/kafka`

## Dépendance
- Nécessite Zookeeper (service `zookeeper`) pour fonctionner correctement.

## Configuration actuelle
- Port exposé : `9092`
- Variables d'environnement :
  - `KAFKA_ADVERTISED_HOST_NAME=kafka`
  - `KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181`
