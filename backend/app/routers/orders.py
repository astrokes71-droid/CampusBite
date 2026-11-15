from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models import MenuItem, Order, OrderItem, User, PaymentLedger, OrderStatusHistory, Review

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
    user: User = Depends(require_role("customer")),
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
        restaurant_ids = set()

        for item_id, quantity in quantities.items():
            food = db.get(MenuItem, item_id)

            if food is None or not food.available:
                raise HTTPException(
                    400, f"Menu item {item_id} is unavailable"
                )

            restaurant_ids.add(food.restaurant_id)
            price = Decimal(str(food.price))
            total += price * quantity
            order_lines.append((item_id, quantity, price))

        if len(restaurant_ids) != 1:
            raise HTTPException(
                400,
                "Please order from one restaurant at a time"
            )

        order = Order(
            user_id=user.id,
            restaurant_id=next(iter(restaurant_ids)),
            total_amount=total,
            status="PLACED",
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

        db.add(PaymentLedger(
            order_id=order.id,
            amount=total,
            payment_status="SUCCESS",
            transaction_type="PAYMENT",
        ))
        db.add(OrderStatusHistory(
            order_id=order.id,
            changed_by=user.id,
            old_status=None,
            new_status="PLACED",
        ))
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
    user: User = Depends(require_role("customer")),
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


class ReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


@router.patch("/{order_id}/cancel")
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("customer")),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id,
    ).with_for_update().first()

    if order is None:
        raise HTTPException(404, "Order not found")

    if order.status != "PLACED":
        raise HTTPException(409, "Only PLACED orders can be cancelled")

    order.status = "CANCELLED"
    db.add(OrderStatusHistory(
        order_id=order.id,
        changed_by=user.id,
        old_status="PLACED",
        new_status="CANCELLED",
    ))
    db.commit()
    return {"order_id": order.id, "status": "CANCELLED"}


@router.post("/{order_id}/review", status_code=201)
def review_order(
    order_id: int,
    payload: ReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("customer")),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id,
    ).first()

    if order is None:
        raise HTTPException(404, "Order not found")

    if order.status != "DELIVERED":
        raise HTTPException(409, "Review allowed after delivery only")

    existing = db.query(Review).filter(
        Review.order_id == order_id,
        Review.user_id == user.id,
    ).first()

    if existing:
        raise HTTPException(409, "Order already reviewed")

    review = Review(
        order_id=order_id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {
        "review_id": review.id,
        "order_id": order_id,
        "rating": review.rating,
        "comment": review.comment,
    }
