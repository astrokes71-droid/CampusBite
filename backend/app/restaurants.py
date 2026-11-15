from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Restaurant

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

@router.get("/")
def get_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "description": r.description
        }
        for r in restaurants
    ]
