# app/api.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Delivery
from app.service import DeliveryService

router = APIRouter()
security = HTTPBearer()
svc = DeliveryService()


def _current_email(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("missing_sub")
        return str(sub).lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


class DeliveryCreateIn(BaseModel):
    reservation_id: str
    item_id: str
    buyer_email: str
    seller_email: str


@router.post("/deliveries")
def create_delivery(
    body: DeliveryCreateIn,
    db: Session = Depends(get_db),
    actor_email: str = Depends(_current_email),
):
    # MVP: solo buyer o seller puede crear
    if actor_email not in {body.buyer_email.lower(), body.seller_email.lower()}:
        raise HTTPException(status_code=403, detail="Only buyer/seller can create delivery")

    delivery = svc.create_delivery(
        db=db,
        reservation_id=body.reservation_id,
        item_id=body.item_id,
        buyer_email=body.buyer_email,
        seller_email=body.seller_email,
    )
    return {
        "ok": True,
        "delivery_id": str(delivery.id),
        "status": delivery.status,
        "buyer_confirmed": delivery.buyer_confirmed,
        "seller_confirmed": delivery.seller_confirmed,
    }


@router.post("/deliveries/{delivery_id}/confirm")
def confirm_delivery(
    delivery_id: str,
    db: Session = Depends(get_db),
    actor_email: str = Depends(_current_email),
):
    try:
        delivery = svc.confirm_delivery(db=db, delivery_id=delivery_id, actor_email=actor_email)
        return {
            "ok": True,
            "delivery_id": str(delivery.id),
            "status": delivery.status,
            "buyer_confirmed": delivery.buyer_confirmed,
            "seller_confirmed": delivery.seller_confirmed,
            "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
        }
    except ValueError as e:
        if str(e) == "delivery_not_found":
            raise HTTPException(status_code=404, detail="Delivery not found")
        raise
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not participant")


@router.get("/deliveries/{delivery_id}")
def get_delivery(
    delivery_id: str,
    db: Session = Depends(get_db),
    actor_email: str = Depends(_current_email),
):
    delivery = db.get(Delivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    if actor_email not in {delivery.buyer_email.lower(), delivery.seller_email.lower()}:
        raise HTTPException(status_code=403, detail="Not participant")

    return {
        "id": str(delivery.id),
        "reservation_id": delivery.reservation_id,
        "item_id": delivery.item_id,
        "buyer_email": delivery.buyer_email,
        "seller_email": delivery.seller_email,
        "buyer_confirmed": delivery.buyer_confirmed,
        "seller_confirmed": delivery.seller_confirmed,
        "status": delivery.status,
        "created_at": delivery.created_at.isoformat(),
        "delivered_at": delivery.delivered_at.isoformat() if delivery.delivered_at else None,
    }
