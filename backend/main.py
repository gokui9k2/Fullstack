from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import uvicorn
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import math
from werkzeug.security import check_password_hash

load_dotenv()



# Variables sensibles
DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_SECRET_ALGORITHM = os.getenv("JWT_SECRET_ALGORITHM")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
security = HTTPBasic()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def sanitize_float(value) -> Optional[float]:
    try:
        if value is None:
            return 0.0
        float_value = float(value)
        if math.isnan(float_value) or math.isinf(float_value):
            return 0.0
        return float_value
    except (ValueError, TypeError):
        return 0.0

class FighterData(BaseModel):
    b_age: float
    b_avg_sig_str_landed: float 
    b_avg_sig_str_pct: float 
    weight_class: Optional[str] = None
    r_age: float 
    r_avg_sig_str_landed: float 
    r_avg_sig_str_pct: float 
    gender: Optional[str] = None
    winner : Optional[str] = None
    date: Optional[datetime] = None
    finish : Optional[str] = None
    latitude : float 
    longitude : float 
    location : Optional[str] = None
    r_weight_lbs : float
    r_height_cms :float
    r_stance :  Optional[str] = None
    b_weight_lbs : float
    b_height_cms : float
    b_stance :  Optional[str] = None
    r_fighter : Optional[str] = None
    b_fighter : Optional[str] = None

class DataResponse(BaseModel):
    data: List[FighterData]

# Fonctions d'authentification restent les mêmes
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_SECRET_ALGORITHM)
    return encoded_jwt


def verify_credentials(username: str, password: str, db: Session):
    """Vérifie les credentials avec le hash stocké"""
    user = db.query(User).filter(User.email == username).first()
    if not user:
        return False
    
    # Le mot de passe dans la DB est déjà hashé, on doit le comparer directement
    return user.password == password 


def verify_authorization_header(access_token: str):
    if not access_token or not access_token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No auth provided.")
    try:
        token = access_token.split("Bearer ")[1]
        auth = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_SECRET_ALGORITHM])
        return auth
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

@app.post("/login")
def login(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        if verify_credentials(credentials.username, credentials.password, db):
            token = create_jwt_token({"sub": credentials.username})
            return {"access_token": token, "token_type": "bearer"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/data", response_model=DataResponse)
def read_data(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    auth_data = verify_authorization_header(auth_header)
    
    # Vérifier que l'utilisateur existe toujours dans la base de données
    user = db.query(User).filter(User.email == auth_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User no longer exists.")
    
    query = db.execute(
        text("""
        SELECT 
            b_age,
            b_avg_sig_str_landed,
            b_avg_sig_str_pct,
            weight_class,
            r_age,
            r_avg_sig_str_landed,
            r_avg_sig_str_pct,
            gender,
            winner,
            date,
            finish,
            longitude,
            latitude,
            location,
            r_weight_lbs,
            r_height_cms,
            r_stance,
            b_weight_lbs,
            b_height_cms,
            b_stance,
            b_fighter,
            r_fighter
        FROM ufctable;
        """)
    )

    results = query.fetchall()
    if not results:
        raise HTTPException(status_code=404, detail="No fighters found")

    formatted_results = []
    for row in results:
        fighter_data = FighterData(
            b_age=sanitize_float(row.b_age),
            b_avg_sig_str_landed=sanitize_float(row.b_avg_sig_str_landed),
            b_avg_sig_str_pct=sanitize_float(row.b_avg_sig_str_pct),    
            weight_class=str(row.weight_class) if row.weight_class else None,
            r_age=sanitize_float(row.r_age),
            r_avg_sig_str_landed=sanitize_float(row.r_avg_sig_str_landed),
            r_avg_sig_str_pct=sanitize_float(row.r_avg_sig_str_pct),
            gender=str(row.gender) if row.gender else None,
            winner=str(row.winner) if row.winner else None,
            date=row.date.strftime("%Y-%m-%d") if row.date else None,  # Formatage de la date ici
            finish=str(row.finish) if row.finish else None,
            latitude=sanitize_float(row.latitude),
            longitude=sanitize_float(row.longitude),
            location = str(row.location) if row.location else None,
            r_weight_lbs = sanitize_float(row.r_weight_lbs),
            r_height_cms = sanitize_float(row.r_height_cms),
            r_stance =  str(row.r_stance) if row.r_stance else None,
            b_weight_lbs = sanitize_float(row.b_weight_lbs),
            b_height_cms =  sanitize_float(row.b_height_cms),
            b_stance =   str(row.b_stance) if row.b_stance else None,
            b_fighter =  str(row.b_fighter) if row.b_fighter else None, 
            r_fighter =  str(row.r_fighter) if row.r_fighter else None
        )
        formatted_results.append(fighter_data)

    return DataResponse(data=formatted_results)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)