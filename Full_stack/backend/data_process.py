
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
from request import get_token, api_request



def data_SIG_STR(df): 

    df_blue = df[["B_age", "B_avg_SIG_STR_landed", "gender"]].rename(columns={"B_age": "Age", "B_avg_SIG_STR_landed": "avg_SIG_STR_landed"})
    df_red = df[["R_age", "R_avg_SIG_STR_landed", "gender"]].rename(columns={"R_age": "Age", "R_avg_SIG_STR_landed": "avg_SIG_STR_landed"})
    df =pd.concat([df_blue, df_red], ignore_index=True)
    df = df.groupby(["Age", "gender"])["avg_SIG_STR_landed"].mean().unstack()
    df = df.reset_index()
    
    return df


def data_weight_class(df): 

    df_blue = df[['B_avg_SIG_STR_pct', "weight_class", "gender"]].rename(columns={'B_avg_SIG_STR_pct': 'avg_SIG_STR_pct'})
    df_red = df[['R_avg_SIG_STR_pct', "weight_class", "gender"]].rename(columns={'R_avg_SIG_STR_pct': 'avg_SIG_STR_pct'})
    
    df_combined = pd.concat([df_blue, df_red], ignore_index=True)
    
    df_male = df_combined[df_combined["gender"] == "MALE"].groupby("weight_class")["avg_SIG_STR_pct"].mean().reset_index()
    df_female = df_combined[df_combined["gender"] == "FEMALE"].groupby("weight_class")["avg_SIG_STR_pct"].mean().reset_index()

    return df_male, df_female



def process() : 
    login_url = "http://localhost:8000/login"
    data_url = "http://localhost:8000/data"
    token = get_token("user", "password", login_url)
    data = api_request(data_url, token)
    df = pd.DataFrame(data['data'])
    df_str = data_SIG_STR(df)
    df_male , df_female = data_weight_class(df)

    return df_str , df_male ,df_female
