from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem

router = APIRouter(prefix="/menu", tags=["Menu"])

@router.get("/")
def get_menu(db: Session = Depends(get_db)):
    items = db.query(MenuItem).all()

    return [
        {
            "id": item.id,
            "restaurant_id": item.restaurant_id,
            "name": item.name,
            "price": float(item.price),
            "available": item.available
        }
        for item in items
    ]

@router.get("/restaurant/{restaurant_id}")
def get_restaurant_menu(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    items = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id
    ).all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "price": float(item.price),
            "available": item.available
        }
        for item in items
    ]
