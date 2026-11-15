from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import MenuItem, Order, OrderStatusHistory, Restaurant, User

router = APIRouter(prefix="/owner", tags=["Restaurant Owner"])


class AvailabilityUpdate(BaseModel):
    available: bool


class OrderStatusUpdate(BaseModel):
    status: str


def owned_restaurant(db, user, restaurant_id):
    restaurant = db.get(Restaurant, restaurant_id)
    if not restaurant:
        raise HTTPException(404, "Restaurant not found")
    if restaurant.owner_id != user.id:
        raise HTTPException(403, "You do not own this restaurant")
    return restaurant


@router.get("/restaurants")
def my_restaurants(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    restaurants = db.query(Restaurant).filter(
        Restaurant.owner_id == user.id
    ).all()

    return [
        {"id": r.id, "name": r.name}
        for r in restaurants
    ]


@router.get("/restaurants/{restaurant_id}/orders")
def restaurant_orders(
    restaurant_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    owned_restaurant(db, user, restaurant_id)

    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant_id
    ).order_by(Order.id.desc()).limit(100).all()

    return [
        {
            "order_id": o.id,
            "status": o.status,
            "total_amount": float(o.total_amount),
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


@router.patch("/menu/{item_id}/availability")
def change_availability(
    item_id: int,
    payload: AvailabilityUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    item = db.get(MenuItem, item_id)

    if not item:
        raise HTTPException(404, "Menu item not found")

    owned_restaurant(db, user, item.restaurant_id)

    item.available = payload.available
    db.commit()

    return {
        "success": True,
        "item_id": item.id,
        "available": item.available,
    }


@router.patch("/orders/{order_id}/status")
def owner_update_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    if order.restaurant_id is None:
        raise HTTPException(409, "Order has no restaurant assigned")

    owned_restaurant(db, user, order.restaurant_id)

    transitions = {
        "PLACED": "ACCEPTED",
        "ACCEPTED": "PREPARING",
        "PREPARING": "READY",
    }

    expected = transitions.get(order.status)

    if expected != payload.status:
        raise HTTPException(
            400,
            f"Invalid transition: {order.status} -> {payload.status}"
        )

    old_status = order.status
    order.status = payload.status

    db.add(OrderStatusHistory(
        order_id=order.id,
        changed_by=user.id,
        old_status=old_status,
        new_status=payload.status,
    ))

    db.commit()

    return {
        "success": True,
        "order_id": order.id,
        "status": order.status,
    }


class DeliveryAssignment(BaseModel):
    delivery_partner_id: int


@router.get("/delivery-partners")
def delivery_partners(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    partners = db.query(User).filter(
        User.role == "delivery_partner"
    ).all()

    return [
        {"id": partner.id, "name": partner.name}
        for partner in partners
    ]


@router.patch("/orders/{order_id}/assign")
def assign_delivery_partner(
    order_id: int,
    payload: DeliveryAssignment,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    if order.restaurant_id is None:
        raise HTTPException(409, "Order has no restaurant")

    owned_restaurant(db, user, order.restaurant_id)

    if order.status != "READY":
        raise HTTPException(
            400, "Only READY orders can be assigned"
        )

    partner = db.get(User, payload.delivery_partner_id)

    if not partner or partner.role != "delivery_partner":
        raise HTTPException(
            400, "Invalid delivery partner"
        )

    order.delivery_partner_id = partner.id
    order.status = "ASSIGNED"

    db.add(OrderStatusHistory(
        order_id=order.id,
        changed_by=user.id,
        old_status="READY",
        new_status="ASSIGNED",
    ))

    db.commit()

    return {
        "success": True,
        "order_id": order.id,
        "delivery_partner_id": partner.id,
        "status": "ASSIGNED",
    }
