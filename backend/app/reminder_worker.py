import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from app.database import SessionLocal
from app.models import AdminReminderLog, Order, OrderStatusHistory

logger = logging.getLogger("campusbite.reminders")


def check_delayed_orders():
    db = SessionLocal()

    try:
        threshold = datetime.now(timezone.utc) - timedelta(minutes=15)

        latest_update = (
            db.query(
                OrderStatusHistory.order_id.label("order_id"),
                func.max(OrderStatusHistory.changed_at).label("last_update"),
            )
            .group_by(OrderStatusHistory.order_id)
            .subquery()
        )

        delayed_orders = (
            db.query(Order)
            .outerjoin(
                latest_update,
                Order.id == latest_update.c.order_id,
            )
            .filter(
                Order.status.in_(["PLACED", "ACCEPTED"]),
                func.coalesce(
                    latest_update.c.last_update,
                    Order.created_at,
                ) < threshold,
            )
            .all()
        )

        created = 0

        for order in delayed_orders:
            existing = (
                db.query(AdminReminderLog)
                .filter(AdminReminderLog.order_id == order.id)
                .first()
            )

            if existing:
                continue

            db.add(AdminReminderLog(
                order_id=order.id,
                message=(
                    f"Order #{order.id} has remained {order.status} "
                    "for more than 15 minutes."
                ),
            ))
            created += 1

        db.commit()

        if created:
            logger.info("Created %s delayed-order reminders", created)

    except Exception:
        db.rollback()
        logger.exception("Background reminder check failed")

    finally:
        db.close()


async def reminder_loop():
    while True:
        await asyncio.to_thread(check_delayed_orders)
        await asyncio.sleep(60)
