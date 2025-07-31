# Zookeeper

Zookeeper est un service de coordination centralisé utilisé principalement par Kafka pour :

- Maintenir la liste des brokers Kafka actifs.
- Gérer le quorum et l’élection du leader Kafka.
- Coordonner les topics, partitions et offsets des consommateurs.

## 🔧 Utilisation

Ce conteneur Zookeeper est utilisé dans le `docker-compose.yml` du projet pour servir de backend de coordination à Kafka.

### Configuration dans `docker-compose.yml`

```yaml
zookeeper:
  image: wurstmeister/zookeeper
  build:
    context: ./services/zookeeper
  ports:
    - "2181:2181"
