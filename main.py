# main.py
import logging
import pytz
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import database, models, schemas, auth

# 1. लॉगिंग सेटअप (कंपनी की बोनस डिमांड)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# डेटाबेस टेबल्स को शुरू में ही क्रिएट करना
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Fitness Studio Booking API")
IST = pytz.timezone('Asia/Kolkata')

# --- 1. POST /signup (यूजर रजिस्ट्रेशन) ---
@app.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: schemas.UserCreate, db: Session = Depends(database.get_db)):
    logger.info(f"Registering new user: {user_data.email}")
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        logger.warning(f"Registration failed: Email {user_data.email} already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth.get_password_hash(user_data.password)
    new_user = models.User(name=user_data.name, email=user_data.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- 2. POST /login (टोकन जनरेशन) ---
@app.post("/login", response_model=schemas.Token)
def login(login_data: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    logger.info(f"Login attempt by: {login_data.email}")
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    if not user or not auth.verify_password(login_data.password, user.hashed_password):
        logger.warning(f"Login failed for: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. POST /classes (क्लास बनाना - ऑथेंटिकेशन ज़रूरी) ---
@app.post("/classes", response_model=schemas.ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: schemas.ClassCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    logger.info(f"Class creation request by admin: {current_user.email}")
    naive_dt = class_data.dateTime
    if naive_dt.tzinfo is None:
        localized_dt = naive_dt.replace(tzinfo=pytz.utc).astimezone(IST)
    else:
        localized_dt = naive_dt.astimezone(IST)

    new_class = models.FitnessClass(
        name=class_data.name,
        instructor=class_data.instructor,
        slots=class_data.availableSlots,
        start_time=localized_dt.replace(tzinfo=None)
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return schemas.ClassResponse(
        id=new_class.id, name=new_class.name, dateTime=localized_dt,
        instructor=new_class.instructor, availableSlots=new_class.slots
    )

# --- 4. GET /classes (सभी क्लासेस की लिस्ट देखना) ---
@app.get("/classes", response_model=List[schemas.ClassResponse])
def get_classes(db: Session = Depends(database.get_db)):
    classes = db.query(models.FitnessClass).all()
    response_list = []
    for c in classes:
        # डेटाबेस से टाइम निकालकर IST टाइमज़ोन टैग जोड़ना
        dt_with_tz = IST.localize(c.start_time)
        response_list.append(schemas.ClassResponse(
            id=c.id, name=c.name, dateTime=dt_with_tz,
            instructor=c.instructor, availableSlots=c.slots
        ))
    return response_list

# --- 5. POST /book (स्लॉट बुक करना - ऑथेंटिकेशन + रूल्स) ---
@app.post("/book", status_code=status.HTTP_201_CREATED)
def book_class(
    booking_data: schemas.BookingCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    logger.info(f"Booking attempt by user: {current_user.email} for class ID: {booking_data.class_id}")
    fitness_class = db.query(models.FitnessClass).filter(models.FitnessClass.id == booking_data.class_id).first()
    if not fitness_class:
        raise HTTPException(status_code=404, detail="Fitness class not found")
    
    # rule 1: ओवरबुकिंग रोकना (एक यूजर एक क्लास को दोबारा बुक न कर सके)
    existing_booking = db.query(models.Booking).filter(
        models.Booking.class_id == booking_data.class_id, models.Booking.user_id == current_user.id
    ).first()
    if existing_booking:
        raise HTTPException(status_code=400, detail="You have already booked a slot in this class")

    # rule 2: चेक करना कि स्लॉट खाली हैं या नहीं
    if fitness_class.slots <= 0:
        raise HTTPException(status_code=400, detail="No available slots left in this class")
    
    new_booking = models.Booking(user_id=current_user.id, class_id=booking_data.class_id)
    fitness_class.slots -= 1  # सीट घटाना
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {
        "message": "Booking successful", "booking_id": new_booking.id,
        "client_name": booking_data.client_name, "client_email": booking_data.client_email,
        "class_name": fitness_class.name
    }

# --- 6. GET /bookings (लॉगिन यूजर की अपनी बुकिंग्स देखना) ---
@app.get("/bookings")
def get_user_bookings(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    bookings = db.query(models.Booking).filter(models.Booking.user_id == current_user.id).all()
    result = []
    for b in bookings:
        dt_with_tz = IST.localize(b.fitness_class.start_time)
        result.append({
            "booking_id": b.id,
            "booking_time": IST.localize(b.booking_time),
            "class_details": {
                "id": b.fitness_class.id, 
                "name": b.fitness_class.name,       # यहाँ कोलन (:) फिक्स कर दिया है
                "instructor": b.fitness_class.instructor, 
                "dateTime": dt_with_tz
            }
        })
    return result

