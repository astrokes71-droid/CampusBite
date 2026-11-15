from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import Order, OrderStatusHistory, Restaurant, User

router = APIRouter(prefix="/delivery", tags=["Delivery Partner"])


class DeliveryStatusUpdate(BaseModel):
    status: str


@router.get("/orders")
def assigned_orders(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("delivery_partner")),
):
    orders = db.query(Order).filter(
        Order.delivery_partner_id == user.id
    ).order_by(Order.id.desc()).all()

    return [
        {
            "order_id": o.id,
            "status": o.status,
            "total_amount": float(o.total_amount),
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


@router.patch("/orders/{order_id}/status")
def update_delivery_status(
    order_id: int,
    payload: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("delivery_partner")),
):
    order = db.get(Order, order_id)

    if not order:
        raise HTTPException(404, "Order not found")

    if order.delivery_partner_id != user.id:
        raise HTTPException(403, "Order not assigned to you")

    transitions = {
        "ASSIGNED": "OUT_FOR_DELIVERY",
        "OUT_FOR_DELIVERY": "DELIVERED",
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
