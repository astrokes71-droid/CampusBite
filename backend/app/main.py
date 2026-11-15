from app.routers import delivery
from app.routers import owner
from app.routers import order_management
from app.routers import orders
from app.routers.payments import router as payments_router
from app.routers.auth import router as auth_router
from app.menu import router as menu_router
from app.restaurants import router as restaurants_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CampusBite API",
    description="Restaurant Ordering and Delivery Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175', 'http://localhost:5176', 'http://localhost:5177', 'http://localhost:5178', 'http://localhost:5179', 'http://localhost:5180', 'http://127.0.0.1:5173', 'http://127.0.0.1:5174', 'http://127.0.0.1:5175', 'http://127.0.0.1:5176', 'http://127.0.0.1:5177', 'http://127.0.0.1:5178', 'http://127.0.0.1:5179', 'http://127.0.0.1:5180'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {
        "message": "Welcome to CampusBite API",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CampusBite Backend"
    }


app.include_router(restaurants_router)


app.include_router(menu_router)

app.include_router(auth_router)


app.include_router(payments_router)

app.include_router(orders.router)

# Temporary order-management router disabled pending authorization

app.include_router(owner.router)

app.include_router(delivery.router)
