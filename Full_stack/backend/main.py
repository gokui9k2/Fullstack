from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Dict, Any  # Ajout de l'importation de Any
import os
import uvicorn
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from typing import Optional 

load_dotenv()

# Configuration de la base de données et de JWT
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://Faker:nigGaTHEcops987@db:5432/UFC_DATABASE")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "should-be-an-environment-variable")
JWT_SECRET_ALGORITHM = os.getenv("JWT_SECRET_ALGORITHM", "HS256")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
security = HTTPBasic()

# Fonction pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modèles Pydantic
class FighterData(BaseModel):
    B_age: Optional[float] = None
    B_avg_SIG_STR_landed: Optional[float] = None
    B_avg_SIG_STR_pct: Optional[float] = None
    weight_class: str
    R_age: Optional[float] = None
    R_avg_SIG_STR_landed: Optional[float] = None
    R_avg_SIG_STR_pct: Optional[float] = None
    gender: str


class DataResponse(BaseModel):
    data: List[FighterData]

# Fonctions d'authentification
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_SECRET_ALGORITHM)
    return encoded_jwt

def verify_credentials(username: str, password: str):
    return username == "user" and password == "password"

def verify_authorization_header(access_token: str):
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No auth provided.")
    try:
        token = access_token.split("Bearer ")[1]
        auth = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_SECRET_ALGORITHM])
        return auth
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

# Routes
@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security)):
    if verify_credentials(credentials.username, credentials.password):
        token = create_jwt_token({"sub": credentials.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/data", response_model=DataResponse)  
def read_data(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    verify_authorization_header(auth_header)
    
    query = db.execute(
        text("""
        SELECT * 
        FROM ufctable;
        """)
    )
    
    results = query.fetchall()
    if not results:
        raise HTTPException(status_code=404, detail="No fighters found")
    
    column_names = query.keys()
    
    formatted_results = [dict(zip(column_names, row)) for row in results]
    
    return {"data": formatted_results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
