from app.routers import reminders
from app.routers import ai_insights
from app.routers import refunds
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

app.include_router(refunds.router)

app.include_router(ai_insights.router)

app.include_router(reminders.router)


import logging
import time
from fastapi import Request

logging.basicConfig(level=logging.INFO)
request_logger = logging.getLogger("campusbite.requests")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        request_logger.exception(
            "API error: %s %s",
            request.method,
            request.url.path
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000

    request_logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms
    )

    return response


# Start the background reminder checker when FastAPI starts.
# Intended for the single-worker academic/demo deployment.
import asyncio
from contextlib import asynccontextmanager

from app.reminder_worker import reminder_loop


@asynccontextmanager
async def campusbite_lifespan(app):
    task = asyncio.create_task(reminder_loop())

    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app.router.lifespan_context = campusbite_lifespan
