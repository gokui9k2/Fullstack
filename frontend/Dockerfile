# Utiliser une image de base Python
FROM python:3.10-slim

# Installer les dépendances nécessaires pour psycopg2 et autres outils de compilation
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt dans l'image
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application dans l'image
COPY . .

# Copier le fichier .env dans l'image (ajoutez cette ligne)
COPY .env ./

# Exposer le port 5000
EXPOSE 5000

# Exécuter l'application avec gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
