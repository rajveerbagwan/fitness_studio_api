# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# स्थानीय SQLite डेटाबेस फ़ाइल का पाथ
SQLALCHEMY_DATABASE_URL = "sqlite:///./fitness_studio.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# हर रिक्वेस्ट के लिए डेटाबेस सेशन खोलने और बंद करने का हेल्पर
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
