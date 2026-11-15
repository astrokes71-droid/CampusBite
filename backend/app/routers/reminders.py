from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import require_role
from app.models import (
    AdminReminderLog, Order, OrderStatusHistory,
    Restaurant, User
)

router = APIRouter(prefix="/owner", tags=["Owner Reminders"])


@router.get("/reminders")
def get_reminders(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("restaurant_owner")),
):
    owned_restaurants = db.query(Restaurant.id).filter(
        Restaurant.owner_id == user.id
    )

    threshold = datetime.now(timezone.utc) - timedelta(minutes=15)

    latest_update = (
        db.query(
            OrderStatusHistory.order_id.label("order_id"),
            func.max(OrderStatusHistory.changed_at).label("last_update")
        )
        .group_by(OrderStatusHistory.order_id)
        .subquery()
    )

    orders = (
        db.query(Order)
        .outerjoin(
            latest_update,
            Order.id == latest_update.c.order_id
        )
        .filter(
            Order.restaurant_id.in_(owned_restaurants),
            Order.status.in_(["PLACED", "ACCEPTED"]),
            func.coalesce(
                latest_update.c.last_update,
                Order.created_at
            ) < threshold,
        )
        .all()
    )

    for order in orders:
        existing = db.query(AdminReminderLog).filter(
            AdminReminderLog.order_id == order.id
        ).first()

        if not existing:
            db.add(AdminReminderLog(
                order_id=order.id,
                message=(
                    f"Order #{order.id} is still {order.status} "
                    "after more than 15 minutes."
                )
            ))

    db.commit()

    reminders = (
        db.query(AdminReminderLog, Order)
        .join(Order, AdminReminderLog.order_id == Order.id)
        .filter(
            Order.restaurant_id.in_(owned_restaurants),
            Order.status.in_(["PLACED", "ACCEPTED"]),
        )
        .order_by(AdminReminderLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "reminder_id": reminder.id,
            "order_id": order.id,
            "status": order.status,
            "message": reminder.message,
            "created_at": reminder.created_at.isoformat(),
        }
        for reminder, order in reminders
    ]
