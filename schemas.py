# schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- CLASS SCHEMAS ---
class ClassCreate(BaseModel):
    name: str
    dateTime: datetime      # नोशन के मुताबिक 'dateTime'
    instructor: str
    availableSlots: int    # नोशन के मुताबिक 'availableSlots'

class ClassResponse(BaseModel):
    id: int
    name: str
    dateTime: datetime
    instructor: str
    availableSlots: int

    class Config:
        from_attributes = True

# --- BOOKING SCHEMAS ---
class BookingCreate(BaseModel):
    class_id: int
    client_name: str       # नोशन के मुताबिक 'client_name'
    client_email: EmailStr # नोशन के मुताबिक 'client_email'
