# Utiliser une image de base Python
FROM python:3.10-slim

# Installer les dépendances nécessaires pour psycopg2 et autres outils de compilation
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Créer un répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt dans l'image
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application dans l'image
COPY . .

# Exposer le port 8000
EXPOSE 8000

# Démarrer le serveur Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
