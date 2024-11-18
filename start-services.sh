echo "Arrêt des conteneurs existants..."
docker-compose down

echo "Démarrage du service API..."
docker-compose up -d db api

echo "Pause de 10 secondes pour laisser l'API démarrer..."
sleep 10

echo "Démarrage du service Frontend..."
docker-compose up -d web

echo "Tous les services sont démarrés!"
echo "Frontend disponible sur http://localhost:5000"
echo "Backend API disponible sur http://localhost:8000"
