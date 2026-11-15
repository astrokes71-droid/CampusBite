from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import (
    Order, Restaurant, User, PaymentLedger, OrderStatusHistory
)

router = APIRouter(prefix="/refunds", tags=["Refunds"])


class RefundRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)


class RefundDecision(BaseModel):
    approved: bool


@router.post("/orders/{order_id}/request", status_code=201)
def request_refund(
    order_id: int,
    payload: RefundRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("customer")),
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id,
    ).with_for_update().first()

    if order is None:
        raise HTTPException(404, "Order not found")

    if order.status != "DELIVERED":
        raise HTTPException(409, "Refund allowed after delivery only")

    existing = db.query(PaymentLedger).filter(
        PaymentLedger.order_id == order_id,
        PaymentLedger.transaction_type == "REFUND",
    ).first()

    if existing:
        raise HTTPException(409, "Refund already requested")

    record = PaymentLedger(
        order_id=order.id,
        amount=order.total_amount,
        payment_status="REQUESTED",
        transaction_type="REFUND",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "refund_id": record.id,
        "order_id": order.id,
        "status": "REQUESTED",
        "reason": payload.reason,
    }


@router.get("/owner/pending")
def pending_refunds(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    rows = (
        db.query(PaymentLedger, Order)
        .join(Order, PaymentLedger.order_id == Order.id)
        .join(Restaurant, Order.restaurant_id == Restaurant.id)
        .filter(
            Restaurant.owner_id == user.id,
            PaymentLedger.transaction_type == "REFUND",
            PaymentLedger.payment_status == "REQUESTED",
        )
        .all()
    )

    return [
        {
            "refund_id": refund.id,
            "order_id": order.id,
            "amount": float(refund.amount),
            "status": refund.payment_status,
        }
        for refund, order in rows
    ]


@router.patch("/owner/{refund_id}/decision")
def decide_refund(
    refund_id: int,
    payload: RefundDecision,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    refund = db.query(PaymentLedger).filter(
        PaymentLedger.id == refund_id,
        PaymentLedger.transaction_type == "REFUND",
    ).with_for_update().first()

    if refund is None:
        raise HTTPException(404, "Refund request not found")

    order = db.query(Order).filter(
        Order.id == refund.order_id
    ).with_for_update().first()

    restaurant = db.get(Restaurant, order.restaurant_id)

    if not restaurant or restaurant.owner_id != user.id:
        raise HTTPException(403, "Not your restaurant")

    if refund.payment_status != "REQUESTED":
        raise HTTPException(409, "Refund already processed")

    if order.status != "DELIVERED":
        raise HTTPException(409, "Order is not eligible for refund")

    if payload.approved:
        refund.payment_status = "APPROVED"
        old_status = order.status
        order.status = "REFUNDED"

        db.add(OrderStatusHistory(
            order_id=order.id,
            changed_by=user.id,
            old_status=old_status,
            new_status="REFUNDED",
        ))
    else:
        refund.payment_status = "REJECTED"

    db.commit()

    return {
        "refund_id": refund.id,
        "order_id": order.id,
        "refund_status": refund.payment_status,
        "order_status": order.status,
        "note": "Demo refund ledger only; no money transferred",
    }
