# test_main.py
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db, Base
import models
from main import app

# 1. टेस्ट के लिए एक फ़ाइल-बेस्ड डेटाबेस पाथ (यह इन-मेमोरी एरर को जड़ से खत्म कर देगा)
TEST_DB_FILE = "./test_fitness.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. डेटाबेस सेशन ओवरराइड फंक्शन
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# 3. हर टेस्ट से पहले क्लीन डेटाबेस तैयार करना और बाद में डिलीट करना
@pytest.fixture(autouse=True)
def setup_database():
    # पुरानी कोई फ़ाइल बची हो तो हटाएँ और नई साफ टेबल्स बनाएं
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # टेस्ट खत्म होने पर टेस्ट डेटाबेस फ़ाइल को क्लीनअप (डिलीट) करना
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass

# --- आपके टेस्ट केसेस ---

def test_signup():
    response = client.post(
        "/signup",
        json={"name": "Rajveer", "email": "rajveer@example.com", "password": "securepassword"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "rajveer@example.com"

def test_login():
    # पहले यूजर बनाएं
    client.post(
        "/signup",
        json={"name": "Rajveer", "email": "rajveer@example.com", "password": "securepassword"}
    )
    # लॉगिन टेस्ट करें
    response = client.post(
        "/login",
        json={"email": "rajveer@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
