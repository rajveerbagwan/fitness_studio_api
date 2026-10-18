### Fitness Studio Booking API

A robust and production-ready **FastAPI** backend application built for a fictional fitness studio management system. 

### Features & Tech Stack

* **Framework:** FastAPI (Auto-generated Swagger UI docs at /docs)
* **Database:** SQLite with SQLAlchemy ORM
* **Authentication:** Secure JWT (JSON Web Tokens) with password hashing (bcrypt)
* **Timezone Management:** All schedules strictly managed in **IST (Asia/Kolkata)**
* **Bonus Features:** Structured logging and automated unit test suite using pytest

### Local Setup Instructions

1. **Clone the repository:** 

bash

git clone <your-github-repo-link>
cd fitness_studio_api

 
2. **Create a virtual environment & activate it:** 

bash

python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

 
3. **Install Dependencies:** 

bash

pip install -r requirements.txt

 
4. **Seed Sample Data (Mandatory Initial Data):**
Run the seed script to populate the database with default upcoming classes: 

bash

python seed.py

 
5. **Run the Application:** 

bash

uvicorn main:app --reload

 

Open http://127.0.0.1:8000/docs to test via the interactive UI.

### Running Unit Tests

To execute the automated unit tests, run: 

bash

pytest

 

### API Usage & cURL Samples

### 1. User Sign Up

bash

curl -X 'POST' \
  'http://127.0.0.1:8000/signup' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Rajveer Bagwan",
  "email": "rajveer@example.com",
  "password": "mysecurepassword"
}'

 

### 2. User Log In (Get JWT Token)

bash

curl -X 'POST' \
  'http://127.0.0.1:8000/login' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "rajveer@example.com",
  "password": "mysecurepassword"
}'

 

*Note: Copy the access_token from the response to use in authenticated endpoints below.* 

### 3. View All Classes

bash

curl -X 'GET' 'http://127.0.0.1:8000/classes'

 

### 4. Book a Class (Requires Bearer Token)

bash

curl -X 'POST' \
  'http://127.0.0.1:8000/book' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN_HERE' \
  -H 'Content-Type: application/json' \
  -d '{
  "class_id": 1,
  "client_name": "Alice",
  "client_email": "alice@example.com"
}'

 

### 5. View Your Bookings (Requires Bearer Token)

bash

curl -X 'GET' \
  'http://127.0.0.1:8000/bookings' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN_HERE'

 