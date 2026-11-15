from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Literal

from app.database import get_db
from app.models import User
from app.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

Role = Literal["customer", "restaurant_owner", "delivery_partner"]


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Literal["customer"] = "customer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = str(data.email).lower()

    existing = db.scalar(
        select(User).where(User.email == email)
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    user = User(
        name=data.name,
        email=email,
        password_hash=hash_password(data.password),
        role=data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful",
        "user_id": user.id,
        "role": user.role
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(
        select(User).where(
            User.email == str(data.email).lower()
        )
    )

    if not user or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id
    }

from app.dependencies import get_current_user, require_role


@router.get("/me")
def get_my_profile(
    user: User = Depends(get_current_user)
):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }


@router.get("/customer-only")
def customer_only(
    user: User = Depends(require_role("customer"))
):
    return {
        "message": "Customer access granted",
        "user_id": user.id
    }


@router.get("/owner-only")
def owner_only(
    user: User = Depends(require_role("restaurant_owner"))
):
    return {
        "message": "Restaurant owner access granted",
        "user_id": user.id
    }


@router.get("/delivery-only")
def delivery_only(
    user: User = Depends(require_role("delivery_partner"))
):
    return {
        "message": "Delivery partner access granted",
        "user_id": user.id
    }
