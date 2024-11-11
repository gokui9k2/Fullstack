#!/bin/bash

# Arrêter tous les conteneurs existants
echo "Arrêt des conteneurs existants..."
docker compose down

# Démarrer le service API et la base de données
echo "Démarrage du service API..."
docker compose up -d api

# Attendre 10 secondes pour laisser à l'API le temps de démarrer
echo "Pause de 10 secondes pour laisser l'API démarrer..."
sleep 10

# Démarrer le service Frontend
echo "Démarrage du service Frontend..."
docker compose up -d web

echo "Tous les services sont démarrés!"
echo "Frontend disponible sur http://localhost:5000"
echo "Backend API disponible sur http://localhost:8000"
