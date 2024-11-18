#!/bin/bash
set -e 

echo "Attente de la base de données..."
python << 'END'
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

async def wait_for_db():
    retries = 0
    while retries < 30:  
        try:
            conn = await asyncpg.connect(f'postgresql://{db_user}:{db_password}@db:5432/{db_name}')
            await conn.close()
            print("✓ Connexion à la base de données établie avec succès")
            return True
        except Exception as e:
            retries += 1
            print(f"Tentative {retries}/30: Base de données pas encore prête... Erreur : {e}")
            await asyncio.sleep(1)
    return False

if not asyncio.run(wait_for_db()):
    print("Échec de la connexion à la base de données après 30 tentatives")
    exit(1)
END

echo "Initialisation de la base de données..."
python insert_data.py

echo "Démarrage de l'application FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

echo "Attente que l'API soit prête..."
while ! curl -s http://localhost:8000/health > /dev/null
do
    echo "L'API n'est pas encore prête..."
    sleep 1
done

echo "✓ L'API est prête !"

tail -f /dev/null
