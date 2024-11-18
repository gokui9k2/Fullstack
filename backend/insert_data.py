import pandas as pd
import asyncio
import asyncpg
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

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
    'location' : ('VARCHAR(50)', str),
    'r_weight_lbs' : ('DOUBLE PRECISION',np.float64),
    'r_height_cms' : ('DOUBLE PRECISION',np.float64),
    'r_stance' :  ('VARCHAR(50)', str),
    'b_weight_lbs' : ('DOUBLE PRECISION',np.float64),
    'b_height_cms' : ('DOUBLE PRECISION',np.float64),
    'b_stance' :  ('VARCHAR(50)', str),
    'r_fighter' : ('VARCHAR(50)' , str),
    'b_fighter' : ('VARCHAR(50)', str)
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

async def table_exists(conn, table_name):
    """Vérifie si une table existe dans la base de données."""
    query = '''
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = $1
        )
    '''
    result = await conn.fetchval(query, table_name)
    return result

async def drop_all_tables(conn):
    try:
        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        for table in tables:
            table_name = table['table_name']
            # Ajout des guillemets doubles pour échapper les noms de table
            await conn.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
            print(f"Table '{table_name}' supprimée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la suppression des tables : {e}")
        raise

async def create_table(conn):
    try:
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
        
        columns = await verify_table_structure(conn)
        expected_columns = set(DTYPE_MAPPING.keys()) | {'id'}
        actual_columns = {col['column_name'] for col in columns}
        
        if not expected_columns.issubset(actual_columns):
            missing = expected_columns - actual_columns
            raise Exception(f"Colonnes manquantes: {missing}")
            
    except Exception as e:
        print(f"Erreur lors de la création de la table : {e}")
        raise

async def create_table_user(conn):
    """Créer une table User si elle n'existe pas déjà."""
    try:
        if not await table_exists(conn, 'users'):  # Changé de 'user' à 'users'
            await conn.execute('''
                CREATE TABLE "users" (  
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            ''')
            print("Table 'users' créée avec succès.")
        else:
            print("La table 'users' existe déjà.")
    except Exception as e:
        print(f"Erreur lors de la création de la table 'users' : {e}")
        raise

# Le reste du code reste inchangé...

async def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df.columns = [col.lower() for col in df.columns]
        
        for column, (_, dtype) in DTYPE_MAPPING.items():
            if column not in df.columns:
                raise ValueError(f"Colonne manquante dans le CSV : {column}")
                
            if dtype == np.float64:
                df[column] = pd.to_numeric(df[column], errors='coerce').fillna(0.0)
            elif dtype == str:
                df[column] = df[column].fillna('').astype(str)
            elif dtype == pd.Timestamp:
                df[column] = pd.to_datetime(df[column], errors='coerce')
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
    try:
        df = pd.read_csv("data_ufc_formatted.csv", encoding='utf-8')
        df = await process_dataframe(df)
        
        db_url = f'postgresql://{db_user}:{db_password}@db:5432/{db_name}'
        pool = await asyncpg.create_pool(db_url)
        
        async with pool.acquire() as conn:
            await drop_all_tables(conn)
            
            await create_table(conn)
            
            await create_table_user(conn)
            
            values = df[list(DTYPE_MAPPING.keys())].values.tolist()
            
            batch_size = 1000
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                await insert_batch(conn, batch)
            
            await verify_data(conn)
        
        await pool.close()
        
    except Exception as e:
        print(f"\nErreur critique lors du traitement : {e}")
        raise

if __name__ == "__main__":
    asyncio.run(insert_data())