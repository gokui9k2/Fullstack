import pandas as pd
import asyncio
import asyncpg
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

# Configuration des types de données
DTYPE_MAPPING = {
    'b_age': ('DOUBLE PRECISION', np.float64),
    'b_avg_sig_str_landed': ('DOUBLE PRECISION', np.float64),
    'b_avg_sig_str_pct': ('DOUBLE PRECISION', np.float64),
    'weight_class': ('VARCHAR(50)', str),
    'r_age': ('DOUBLE PRECISION', np.float64),
    'r_avg_sig_str_landed': ('DOUBLE PRECISION', np.float64),
    'r_avg_sig_str_pct': ('DOUBLE PRECISION', np.float64),
    'gender': ('VARCHAR(10)', str),
    'winner': ('VARCHAR(50)', str),
    'date': ('TIMESTAMP', pd.Timestamp),
    'finish': ('VARCHAR(50)', str),
    'latitude': ('DOUBLE PRECISION', np.float64),
    'longitude': ('DOUBLE PRECISION', np.float64),
    'location' : ('VARCHAR(50)', str)
}

async def verify_table_structure(conn) -> List[Dict[str, Any]]:
    """Vérifie la structure de la table et retourne les détails des colonnes."""
    columns = await conn.fetch("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = 'ufctable'
        ORDER BY ordinal_position;
    """)
    print("\nStructure actuelle de la table ufctable:")
    for col in columns:
        print(f"Colonne: {col['column_name']}")
        print(f"Type: {col['data_type']}")
        print(f"Longueur max: {col['character_maximum_length']}")
        print("---")
    return columns

async def drop_all_tables(conn):
    """Supprime toutes les tables existantes."""
    try:
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        for table in tables:
            table_name = table['table_name']
            await conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
            print(f"Table '{table_name}' supprimée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la suppression des tables : {e}")
        raise

async def create_table(conn):
    """Crée la table ufctable avec la structure appropriée."""
    try:
        # Construction de la requête de création de table
        columns_def = [f"id SERIAL PRIMARY KEY"]
        columns_def.extend([
            f"{col_name} {sql_type}"
            for col_name, (sql_type, _) in DTYPE_MAPPING.items()
        ])
        
        create_query = f"""
        CREATE TABLE ufctable (
            {','.join(columns_def)}
        );
        """
        
        await conn.execute(create_query)
        print("Table 'ufctable' créée avec succès.")
        
        # Vérification de la création
        columns = await verify_table_structure(conn)
        expected_columns = set(DTYPE_MAPPING.keys()) | {'id'}
        actual_columns = {col['column_name'] for col in columns}
        
        if not expected_columns.issubset(actual_columns):
            missing = expected_columns - actual_columns
            raise Exception(f"Colonnes manquantes: {missing}")
            
    except Exception as e:
        print(f"Erreur lors de la création de la table : {e}")
        raise

async def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Traite le DataFrame pour assurer la conformité des types de données."""
    try:
        # Conversion des noms de colonnes en minuscules
        df.columns = [col.lower() for col in df.columns]
        
        # Application des types de données
        for column, (_, dtype) in DTYPE_MAPPING.items():
            if column not in df.columns:
                raise ValueError(f"Colonne manquante dans le CSV : {column}")
                
            if dtype == np.float64:
                df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0.0)
            elif dtype == str:
                df[column] = df[column].fillna('').astype(str)
            elif dtype == pd.Timestamp:
                # Convertir la colonne en datetime, en gérant les erreurs avec 'coerce'
                df[column] = pd.to_datetime(df[column], errors='coerce')
                # Si une date est mal formatée, la remplacer par '1900-01-01'
                df[column] = df[column].fillna(pd.Timestamp('1900-01-01'))
        
        return df
    except Exception as e:
        print(f"Erreur lors du traitement du DataFrame : {e}")
        raise


async def insert_batch(conn, batch_values: List[List[Any]]):
    """Insère un lot de données dans la table."""
    try:
        columns = list(DTYPE_MAPPING.keys())
        placeholders = ','.join(f'${i+1}' for i in range(len(columns)))
        
        insert_query = f"""
        INSERT INTO ufctable (
            {','.join(columns)}
        ) VALUES ({placeholders})
        """
        
        await conn.executemany(insert_query, batch_values)
        print(f"Lot de {len(batch_values)} lignes inséré avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'insertion du lot : {e}")
        raise

async def verify_data(conn):
    """Vérifie les données insérées."""
    try:
        count = await conn.fetchval("SELECT COUNT(*) FROM ufctable;")
        print(f"\nNombre total de lignes dans la table: {count}")
        
        if count > 0:
            sample = await conn.fetch("SELECT * FROM ufctable LIMIT 5;")
            print("\nÉchantillon de données:")
            for row in sample:
                print(row)
    except Exception as e:
        print(f"Erreur lors de la vérification des données : {e}")
        raise

async def insert_data():
    """Fonction principale pour l'insertion des données."""
    try:
        # Lecture du CSV
        print("Lecture du fichier CSV...")
        df = pd.read_csv("data_ufc.csv", encoding='utf-8')
        df = await process_dataframe(df)
        
        # Connexion à la base de données
        print("\nConnexion à la base de données...")
        db_url = 'postgresql://Faker:nigGaTHEcops987@db:5432/UFC_DATABASE'
        pool = await asyncpg.create_pool(db_url)
        
        async with pool.acquire() as conn:
            # Suppression des tables existantes
            print("\nSuppression des tables existantes...")
            await drop_all_tables(conn)
            
            # Création de la nouvelle table
            print("\nCréation de la nouvelle table...")
            await create_table(conn)
            
            # Préparation et insertion des données
            print("\nInsertion des données...")
            values = df[list(DTYPE_MAPPING.keys())].values.tolist()
            
            batch_size = 1000
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                await insert_batch(conn, batch)
            
            # Vérification finale
            print("\nVérification finale des données...")
            await verify_data(conn)
        
        await pool.close()
        print("\nTraitement terminé avec succès!")
        
    except Exception as e:
        print(f"\nErreur critique lors du traitement : {e}")
        raise

if __name__ == "__main__":
    asyncio.run(insert_data())