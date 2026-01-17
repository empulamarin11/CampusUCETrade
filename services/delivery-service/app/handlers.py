# app/handlers.py
from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.service import DeliveryService
from app.models import Delivery

svc = DeliveryService()


def _email_from_token(token: str) -> str:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    sub = payload.get("sub")
    if not sub:
        raise ValueError("token_missing_sub")
    return str(sub).lower()


def handle_create(db: Session, payload: dict) -> dict:
    for k in ["reservation_id", "item_id", "buyer_email", "seller_email"]:
        if k not in payload:
            raise ValueError(f"missing_{k}")

    delivery: Delivery = svc.create_delivery(
        db=db,
        reservation_id=payload["reservation_id"],
        item_id=payload["item_id"],
        buyer_email=payload["buyer_email"],
        seller_email=payload["seller_email"],
    )

    return {"ok": True, "delivery_id": str(delivery.id), "status": delivery.status}


def handle_confirm(db: Session, payload: dict) -> dict:
    for k in ["delivery_id", "token"]:
        if k not in payload:
            raise ValueError(f"missing_{k}")

    actor_email = _email_from_token(payload["token"])

    delivery: Delivery = svc.confirm_delivery(
        db=db,
        delivery_id=payload["delivery_id"],
        actor_email=actor_email,
    )

    return {
        "ok": True,
        "delivery_id": str(delivery.id),
        "status": delivery.status,
        "buyer_confirmed": delivery.buyer_confirmed,
        "seller_confirmed": delivery.seller_confirmed,
        "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
    }
