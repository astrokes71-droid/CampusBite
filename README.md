# CampusBite

A full-stack food ordering and restaurant management application developed for the Masai School E&ICT IIT Roorkee Software Engineering with AI program.

## Technology Stack

- Frontend: React, Vite, JavaScript, Axios
- Backend: Python, FastAPI, SQLAlchemy
- Database: PostgreSQL
- Authentication: JWT
- Deployment: Docker and Docker Compose
- AI Integration: OpenAI API (requires a configured API key)

## Features

### Customer
- Account registration and login
- Browse restaurant menus
- Add food items to cart
- Place orders using dummy checkout
- View order history
- Cancel eligible orders
- Review delivered orders
- Request refunds
- Ask AI questions about previous orders

### Restaurant Owner
- View restaurant orders
- Update order preparation status
- Manage dish availability
- Create and edit menu items
- Assign delivery partners
- Review and decide refund requests
- View delayed-order reminders

### Delivery Partner
- View assigned orders
- Update delivery status
- Complete deliveries

## Order Lifecycle

PLACED -> ACCEPTED -> PREPARING -> READY -> ASSIGNED -> OUT_FOR_DELIVERY -> DELIVERED

Other supported states include CANCELLED and REFUNDED.

## Running Locally

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Backend documentation:
http://localhost:8000/docs

The backend requires a configured PostgreSQL database and environment variables.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite.

### Docker

Create a root `.env` file with the required environment variables, including `POSTGRES_PASSWORD` and `JWT_SECRET_KEY`.

```bash
docker compose up -d --build
docker compose ps
```

The Docker backend is exposed on port 8001 in the current configuration.

## Security

- JWT-based authentication
- Role-based backend authorization
- Environment variables for secrets
- Password hashing
- No real payment processing is required for dummy checkout

## AI Configuration

Set `OPENAI_API_KEY` in the backend environment to enable AI order insights.

AI requests require an available OpenAI API account and appropriate API credits.

## Project Status

Core customer, owner, and delivery features have been implemented. Final workflow, deployment, and requirement-compliance testing is ongoing.

## Repository

https://github.com/astrokes71-droid/CampusBite
