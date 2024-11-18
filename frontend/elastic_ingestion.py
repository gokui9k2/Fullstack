from elasticsearch import Elasticsearch, helpers
import pandas as pd
import numpy as np
import logging
from typing import Iterator, Dict, Any
import os 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_es_client() -> Elasticsearch:
    return Elasticsearch(
        ['http://elasticsearch:9200'],
        timeout=30,
        retry_on_timeout=True,
        max_retries=3
    )


MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "nom": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "gender": {"type": "keyword"},
            "avg_sig_str_landed": {"type": "float"},
            "height_cms": {"type": "float"},
            "stance": {"type": "keyword"},
            "weight_lbs": {"type": "float"},
            "date": {"type": "date"},
            "color": {"type": "keyword"},
            "DQ": {"type": "integer"},
            "KO/TKO": {"type": "integer"},
            "M-DEC": {"type": "integer"},
            "Overturned" : {"type" : "integer"}, 
            "S-DEC" : {"type" : "integer"}, 
            "SUB" : {"type" : "integer"},
            "U-DEC" : {"type" : "integer"} 

        }
    }
}

def fighter_data(df):
    df["r_gender"] = df["gender"]
    df["b_gender"] = df["gender"]
    df["r_date"] = df["date"]
    df["b_date"] = df["date"]
    
    winners = np.where(df['winner'] == 'Red', df['r_fighter'],
                      np.where(df['winner'] == 'Blue', df['b_fighter'], None))
    

    result_df = pd.DataFrame({'Nom': winners, 'finish': df['finish']})
    result_df = result_df.dropna()
    result_df = result_df.groupby('Nom')['finish'].agg(list).reset_index()
    summary_df = result_df.explode('finish').groupby(['Nom', 'finish']).size().unstack(fill_value=0)
    summary_df = summary_df.reset_index()
    summary_df = summary_df.rename(columns={'Nom': 'nom'})
    

    red_df = df[["r_fighter", "r_gender", "r_avg_sig_str_landed", "r_height_cms", 
                 "r_stance", "r_weight_lbs", "r_date"]]
    red_df.columns = ["nom", "gender", "avg_sig_str_landed", "height_cms", 
                      "stance", "weight_lbs", "date"]
    red_df["color"] = "Red"
    
    blue_df = df[["b_fighter", "b_gender", "b_avg_sig_str_landed", "b_height_cms", 
                  "b_stance", "b_weight_lbs", "b_date"]]
    blue_df.columns = ["nom", "gender", "avg_sig_str_landed", "height_cms", 
                       "stance", "weight_lbs", "date"]
    blue_df["color"] = "Blue"
    
    combined_df = pd.concat([red_df, blue_df], ignore_index=True)
    combined_df['date'] = pd.to_datetime(combined_df['date'])
    combined_df = combined_df.sort_values(["nom", "date"], ascending=[True, False])
    
    latest_df = combined_df.drop_duplicates(subset="nom", keep="first")
    latest_df = latest_df.reset_index(drop=True)
    
    result_df = latest_df.merge(summary_df, on='nom', how='left')
    
    numeric_cols = result_df.select_dtypes(include=['number']).columns
    text_cols = result_df.select_dtypes(include=['object', 'category']).columns
    
    result_df[numeric_cols] = result_df[numeric_cols].fillna(-1)
    result_df[text_cols] = result_df[text_cols].fillna("N/A")
    
    return result_df


def doc_generator(df: pd.DataFrame, chunk_size: int = 500) -> Iterator[Dict[str, Any]]:
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        for _, row in chunk.iterrows():
            doc = {
                "_index": "combattants",
                "_source": {k: str(v) if pd.isna(v) else v for k, v in row.to_dict().items()}
            }
            yield doc

def create_index(es: Elasticsearch, index_name: str) -> None:
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=MAPPING)
        logger.info(f"Index {index_name} created with mapping")

def main(df):
    try:
        es = create_es_client()
        
        if not es.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        
        processed_df = fighter_data(df)
        print(processed_df)
        create_index(es, "combattants")
        
        success, failed = 0, 0
        for ok, item in helpers.parallel_bulk(
            es,
            doc_generator(processed_df),
            chunk_size=500,
            raise_on_error=False,
            raise_on_exception=False
        ):
            if ok:
                success += 1
            else:
                failed += 1
                logger.error(f"Failed to index document: {item}")
        
        logger.info(f"Indexed {success} documents successfully. Failed: {failed}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise


