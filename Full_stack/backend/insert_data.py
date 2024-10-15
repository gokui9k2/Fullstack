import pandas as pd
from sqlalchemy import create_engine

def insert_data():
    df = pd.read_csv("data_ufc.csv")
    
    df.columns = [col.lower() for col in df.columns]
    
    db_url = 'postgresql+psycopg2://Faker:nigGaTHEcops987@db:5432/UFC_DATABASE'
    engine = create_engine(db_url)
    table_name = 'ufctable'
    df.to_sql(table_name, engine, if_exists='append', index=False)

insert_data()