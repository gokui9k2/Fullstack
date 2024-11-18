from flask import Flask, render_template, request, jsonify, redirect, url_for,session
import pandas as pd
import numpy as np
import os
import sys
import json
from data_process import process
from elasticsearch import Elasticsearch
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import secrets
from functools import wraps

load_dotenv()

db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@db:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secrets.token_hex(16)


db = SQLAlchemy(app)

es = Elasticsearch(hosts=['http://elasticsearch:9200'])



class User(db.Model):
    __tablename__ = 'users'  # Nom de la table existante
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400

            new_user = User(email=email)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            return jsonify({'message': 'User registered successfully'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return render_template('register.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                return redirect(url_for('index'))
            else:
                return jsonify({'error': 'Invalid email or password'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('login.html')

@app.route('/search', methods=['GET'])
def search():
    fighter_name = request.args.get('fighter_name', '')
    if len(fighter_name) < 2:
        return jsonify(error="Veuillez entrer au moins deux lettres.")

    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase_prefix": {
                            "nom": {
                                "query": fighter_name,
                                "max_expansions": 10
                            }
                        }
                    },
                    {
                        "fuzzy": {
                            "nom": {
                                "value": fighter_name,
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ]
            }
        },
        "_source": ["nom", "gender", "avg_sig_str_landed", "height_cms", "stance", 
                   "weight_lbs", "date", "DQ", "KO/TKO", "M-DEC", "Overturned", 
                   "S-DEC", "SUB", "U-DEC"]
    }

    try:
        response = es.search(index='combattants', body=query)
        results = []
        for hit in response['hits']['hits']:
            source = hit['_source']
            fighter = {
                'nom': source.get('nom', 'N/A'),
                'gender': source.get('gender', 'N/A'),
                'height_cms': source.get('height_cms', 'N/A'),
                'stance': source.get('stance', 'N/A'),
                'weight_lbs': source.get('weight_lbs', 'N/A'),
                'DQ': source.get('DQ', 'N/A'),
                'KO/TKO': source.get('KO/TKO', 'N/A'),
                'M-DEC': source.get('M-DEC', 'N/A'),
                'Overturned': source.get('Overturned', 'N/A'),
                'S-DEC': source.get('S-DEC', 'N/A'),
                'SUB': source.get('SUB', 'N/A'),
                'U-DEC': source.get('U-DEC', 'N/A')
            }
            results.append(fighter)

        return jsonify(results=results)
    except Exception as e:
        return jsonify(error=f"Erreur: {str(e)}")


@app.route('/')
@login_required 
def index():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    df_str, df_male, df_female, red_blue, finish_rat, ufc_love, influnce_carte, gender_disparity = process(user)
    
    heatmap_male_html = create_heatmap(df_male, new_order_male)
    heatmap_female_html = create_heatmap(df_female, new_order_female)    
    line_plot_female, line_plot_male = create_line_plot(df_str)
    winner_ratio = red_blue.to_dict()
    finish_ratio = finish_rat.to_dict()
    coordinates = json.dumps(influnce_carte)
    ufc_love_json = json.dumps(ufc_love)
    gender_data = json.dumps(gender_disparity)  
    finish_ratio_json = json.dumps(finish_ratio)
    winner_rat_json = json.dumps(winner_ratio)
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
        winner_rat=winner_rat_json,
        finish_ratio=finish_ratio_json,
        coordinates=coordinates,
        gender_disparity=gender_data,
        ufc_love = ufc_love_json  
    )


if __name__ == '__main__':
    app.run(debug=True) 
