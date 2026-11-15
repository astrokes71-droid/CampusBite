from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import MenuItem, Order, OrderItem, User

router = APIRouter(prefix="/orders", tags=["Orders"])


class CartItem(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1, le=100)


class CheckoutRequest(BaseModel):
    items: List[CartItem] = Field(min_length=1)


@router.post("/demo-checkout", status_code=201)
def demo_checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        quantities = {}
        for item in payload.items:
            quantities[item.menu_item_id] = (
                quantities.get(item.menu_item_id, 0) + item.quantity
            )

        if any(q > 100 for q in quantities.values()):
            raise HTTPException(400, "Quantity limit exceeded")

        order_lines = []
        total = Decimal("0.00")

        for item_id, quantity in quantities.items():
            food = db.get(MenuItem, item_id)

            if food is None or not food.available:
                raise HTTPException(
                    400, f"Menu item {item_id} is unavailable"
                )

            price = Decimal(str(food.price))
            total += price * quantity
            order_lines.append((item_id, quantity, price))

        order = Order(
            user_id=user.id,
            total_amount=total,
            status="demo_paid",
        )
        db.add(order)
        db.flush()

        for item_id, quantity, price in order_lines:
            db.add(
                OrderItem(
                    order_id=order.id,
                    menu_item_id=item_id,
                    quantity=quantity,
                    unit_price=price,
                )
            )

        db.commit()
        db.refresh(order)

        return {
            "success": True,
            "order_id": order.id,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "message": "Demo order saved successfully",
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save demo order",
        )


@router.get("/history")
def get_order_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )

    result = []

    for order in orders:
        items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        result.append({
            "order_id": order.id,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "menu_item_id": item.menu_item_id,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                }
                for item in items
            ],
        })

    return result
