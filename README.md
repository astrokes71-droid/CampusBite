# CampusBite

### Campus Food Ordering Web Application

CampusBite is a full-stack web application designed to help students browse campus food menus, manage shopping carts, place demo orders, and review their order history.

## Technology Stack

**Frontend**
- React
- Vite
- JavaScript
- CSS

**Backend**
- Python
- FastAPI
- SQLAlchemy
- JWT Authentication

**Database**
- PostgreSQL
- Psycopg

**Development Tools**
- Git and GitHub
- Docker and Docker Compose

## Implemented Features

- User registration and login
- JWT-based authentication
- Role-based authentication endpoints
- Restaurant and food menu APIs
- Food images and menu prices
- Shopping cart management
- Item quantity selection
- Total price calculation
- Demo checkout
- Order storage in PostgreSQL
- Authenticated order history
- Order details including food names, quantities, prices and statuses
- Backend health-check endpoint

## Project Structure

    CampusBite/
    ├── backend/
    │   ├── app/
    │   ├── Dockerfile
    │   └── requirements.txt
    ├── frontend/
    │   ├── src/
    │   └── package.json
    ├── docker-compose.yml
    ├── .env.example
    └── README.md

## Local Installation

### Backend

Install Python and PostgreSQL.

    cd backend
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Create backend/.env using backend/.env.example.

Configure DATABASE_URL and JWT_SECRET_KEY.

Ensure the PostgreSQL database has the required tables and initial menu data.

Start the backend:

    python -m uvicorn app.main:app --reload --port 8000

Backend URL:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

### Frontend

    cd frontend
    npm install
    npm run dev

Open the local URL displayed by Vite.

## Main API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Backend health |
| POST | /auth/register | User registration |
| POST | /auth/login | User login |
| GET | /auth/me | Current user |
| POST | /orders/demo-checkout | Demo order checkout |
| GET | /orders/history | Authenticated order history |
| POST | /payments/create-order | Payment order creation |

Additional restaurant and menu endpoints are available in the FastAPI documentation.

## Payment Information

CampusBite includes a demo checkout workflow that saves orders to PostgreSQL.

A Razorpay payment-order API is also present. Successful live payment processing and verification are not claimed as completed features.

## Docker

Docker configuration files are included for the FastAPI backend and PostgreSQL.

The containerized setup requires environment configuration, database initialization, and integration testing before it can be considered verified.

## Security

- JWT-based authentication
- Environment variables for credentials
- Private .env files excluded from Git
- Development backups excluded from Git

Do not commit real database passwords, JWT secrets or payment API credentials.

## Testing

Frontend production build:

    cd frontend
    npm run build

Backend API documentation:

http://127.0.0.1:8000/docs

## Future Improvements

- Complete payment verification
- Restaurant management dashboard
- Delivery tracking
- Admin dashboard
- Production deployment
- Automated testing

## Academic Project

Developed as part of the Software Engineering with AI learning program associated with Masai School and E&ICT Academy, IIT Roorkee.

## Project Status

Core application workflow implemented and locally tested.

Docker deployment and production hosting require further verification.
