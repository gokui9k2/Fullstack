from flask import Flask, render_template
import pandas as pd
import numpy as np
import os
import sys
import json
import uvicorn

# Importez ensuite votre module
from data_process import process


app = Flask(__name__)

df_str, df_male, df_female, red_blue, finish_rat, ufc_love, influnce_carte, gender_disparity = process()
print(gender_disparity)

new_order_male = ['Flyweight', 'Bantamweight', 'Featherweight', 'Lightweight', 'Welterweight', 'Middleweight', 'Light Heavyweight', 'Heavyweight']
new_order_female = ["Women's Strawweight", "Women's Bantamweight", "Women's Featherweight", "Women's Flyweight"]

def create_heatmap(df, order):
    df = df.replace({None: np.nan})
    df = df.dropna(subset=['avg_SIG_STR_pct'])
    df['avg_SIG_STR_pct'] = df['avg_SIG_STR_pct'].apply(lambda x: round(x, 2))
    df['weight_class'] = pd.Categorical(df['weight_class'], categories=order, ordered=True)
    df_sorted = df.sort_values('weight_class')
    heatmap_data = df_sorted[['weight_class', 'avg_SIG_STR_pct']]
    heatmap_data = heatmap_data.dropna(subset=['weight_class', 'avg_SIG_STR_pct'])

    heatmap_dict = {
        "order": order,
        "heatmap_data": heatmap_data.to_dict(orient="list")
    }
    return heatmap_dict

def create_line_plot(df):
    df = df.replace({None: np.nan})
    df = df.dropna(subset=['FEMALE', 'MALE'])
    df['FEMALE'] = df['FEMALE'].apply(lambda x: round(x, 2))
    df['MALE'] = df['MALE'].apply(lambda x: round(x, 2))
    df_melted = df.melt(id_vars='Age', value_vars=['FEMALE', 'MALE'], var_name='gender', value_name='value')
    dict_female = {"gender": "FEMALE",
        "data": df_melted[df_melted["gender"] == "FEMALE"]['value'].tolist(),
        "Age": df_melted[df_melted["gender"] == "FEMALE"]['Age'].tolist()}
    dict_male = {"gender": "MALE",
        "data": df_melted[df_melted["gender"] == "MALE"]['value'].tolist(),
        "Age": df_melted[df_melted["gender"] == "MALE"]['Age'].tolist()}
    return dict_male, dict_female


@app.route('/')
def index():
    # Générer les HTML pour les graphiques
    heatmap_male_html = create_heatmap(df_male, new_order_male)
    heatmap_female_html = create_heatmap(df_female, new_order_female)    
    line_plot_female, line_plot_male = create_line_plot(df_str)
    winner_ratio = red_blue.to_dict()
    finish_ratio = finish_rat.to_dict()
    coordinates = json.dumps(influnce_carte)

    gender = json.dumps(gender_disparity)
    finish_ratio = json.dumps(finish_ratio)
    winner_rat = json.dumps(winner_ratio)
    line_plot_female_json = json.dumps(line_plot_female)
    line_plot_male_json = json.dumps(line_plot_male)
    heatmap_female_html_json = json.dumps(heatmap_female_html)
    heatmap_male_html_json = json.dumps(heatmap_male_html)

    return render_template(
    'index.html',
    heatmap_male=heatmap_male_html_json,
    heatmap_female=heatmap_female_html_json,
    line_plot_female=line_plot_female_json,
    line_plot_male=line_plot_male_json,
    winner_rat=winner_rat,
    finish_ratio=finish_ratio,
    coordinates=coordinates,
    gender_disparity=gender  # Ici, changez "gender" en "gender_disparity"
)

if __name__ == '__main__':
    app.run(debug=True) 
