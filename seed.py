# seed.py
import pytz
from datetime import datetime, timedelta
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    if db.query(models.FitnessClass).count() > 0:
        print("Database already has sample data.")
        db.close()
        return

    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)

    sample_classes = [
        models.FitnessClass(name="Yoga Flow", instructor="John Doe", slots=20, start_time=(now + timedelta(days=1)).replace(tzinfo=None)),
        models.FitnessClass(name="Zumba Dance", instructor="Jane Smith", slots=15, start_time=(now + timedelta(days=2)).replace(tzinfo=None)),
        models.FitnessClass(name="HIIT Session", instructor="Mike Tyson", slots=10, start_time=(now + timedelta(days=3)).replace(tzinfo=None))
    ]
    db.add_all(sample_classes)
    db.commit()
    print("Successfully seeded sample data into the database! 🌱")
    db.close()

if __name__ == "__main__":
    seed_data()
