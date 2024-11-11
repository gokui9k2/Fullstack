# Utiliser une image de base Python
FROM python:3.10-slim

# Installer les dépendances nécessaires pour psycopg2, autres outils de compilation, et curl
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt dans l'image
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application dans l'image
COPY . .

# Copier le script shell (script.sh) dans l'image
COPY script.sh /app/script.sh

# Rendre le script exécutable
RUN chmod +x /app/script.sh

# Exposer le port 8000
EXPOSE 8000

# Définir la variable d'environnement pour indiquer à Python de ne pas mettre en mémoire tampon la sortie
ENV PYTHONUNBUFFERED=1

# Exécuter le script shell au démarrage du conteneur
CMD ["/bin/bash", "/app/script.sh"]
