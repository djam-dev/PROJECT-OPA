# Utiliser une image Python légère basée sur Debian
FROM python:3.10-buster


# 🔧 Patch pour les sources Debian archivées
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|http://archive.debian.org/|g' /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until




# Installer les bibliothèques système nécessaires
RUN apt-get update && apt-get install -y \
    librdkafka-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Créer le dossier de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances Python
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code du projet
COPY . /app

# S'assurer que le modèle ML est inclus pour FastAPI
COPY model.pkl /app/model.pkl

# Exposer les ports utiles
EXPOSE 8000
EXPOSE 8888
# Pas de CMD ici : chaque service définit sa commande dans docker-compose.yml
