import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Float, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import jwt
import os
from datetime import datetime, timedelta
import pandas as pd

from main import app, Base, get_db, User, create_jwt_token
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_SECRET_ALGORITHM = os.getenv("JWT_SECRET_ALGORITHM")

class UFCTable(Base):
    __tablename__ = 'ufctable'
    
    b_age = Column(Float, nullable=True)
    b_avg_sig_str_landed = Column(Float, nullable=True)
    b_avg_sig_str_pct = Column(Float, nullable=True)
    weight_class = Column(String, nullable=True)
    r_age = Column(Float, nullable=True)
    r_avg_sig_str_landed = Column(Float, nullable=True)
    r_avg_sig_str_pct = Column(Float, nullable=True)
    gender = Column(String, nullable=True)
    winner = Column(String, nullable=True)
    date = Column(DateTime, nullable=True)
    finish = Column(String, nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    r_weight_lbs = Column(Float, nullable=True)
    r_height_cms = Column(Float, nullable=True)
    r_stance = Column(String, nullable=True)
    b_weight_lbs = Column(Float, nullable=True)
    b_height_cms = Column(Float, nullable=True)
    b_stance = Column(String, nullable=True)
    b_fighter = Column(String, nullable=True)
    r_fighter = Column(String, nullable=True)
    id = Column(Integer, primary_key=True, autoincrement=True)

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    
    try:
        csv_path = 'data_ufc_formatted.csv'
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        df = pd.read_csv(csv_path)
        df.columns = [col.lower() for col in df.columns]
        test_user = User(
            email="test@example.com", 
            password="testpassword"
        )
        db.add(test_user)
        db.commit()
    
    except Exception as e:
        db.rollback()
        pytest.fail(f"Database setup error: {e}")
    
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_login_success(db):
    response = client.post("/login", auth=("test@example.com", "testpassword"))
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()

def test_login_failure(db):
    response = client.post("/login", auth=("wrong@example.com", "wrongpassword"))
    assert response.status_code == 401

def test_data_access_unauthorized():
    response = client.get("/data")
    assert response.status_code == 401

def test_invalid_token(db):
    invalid_token = jwt.encode(
        {"sub": "fake@example.com", "exp": datetime.utcnow() + timedelta(minutes=30)}, 
        "wrong_secret_key"
    )
    
    response = client.get("/data", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401

def test_token_expiration(db):
    expired_token = jwt.encode(
        {"sub": "test@example.com", "exp": datetime.utcnow() - timedelta(minutes=31)}, 
        os.getenv("JWT_SECRET_KEY")
    )
    
    response = client.get("/data", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401