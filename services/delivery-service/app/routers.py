import os
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Delivery

router = APIRouter(tags=["delivery"])

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()


def get_current_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token missing subject")
        return str(email).lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


class DeliveryStatus(str, Enum):
    created = "created"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"


class DeliveryCreate(BaseModel):
    reservation_id: str = Field(min_length=1)
    # MVP: we still don't call reservation-service, so we receive buyer/seller emails directly
    seller_email: str = Field(min_length=5)
    buyer_email: str = Field(min_length=5)
    carrier: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)


class DeliveryOut(BaseModel):
    id: str
    reservation_id: str
    seller_email: str
    buyer_email: str
    status: DeliveryStatus
    carrier: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class DeliveryUpdateStatus(BaseModel):
    status: DeliveryStatus


@router.get("/health")
def health():
    return {"status": "ok", "service": "delivery-service"}


@router.post("/", response_model=DeliveryOut)
def create_delivery(
    payload: DeliveryCreate,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    # Only seller can create delivery
    if me != payload.seller_email.lower():
        raise HTTPException(status_code=403, detail="Not allowed")

    now = datetime.now(timezone.utc)
    delivery_id = str(uuid4())

    row = Delivery(
        id=delivery_id,
        reservation_id=payload.reservation_id,
        seller_email=payload.seller_email.lower(),
        buyer_email=payload.buyer_email.lower(),
        status=DeliveryStatus.created.value,
        carrier=payload.carrier,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()

    return DeliveryOut(
        id=row.id,
        reservation_id=row.reservation_id,
        seller_email=row.seller_email,
        buyer_email=row.buyer_email,
        status=DeliveryStatus(row.status),
        carrier=row.carrier,
        notes=row.notes,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
        updated_at=row.updated_at.isoformat().replace("+00:00", "Z"),
    )


@router.get("/", response_model=List[DeliveryOut])
def list_deliveries(
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    stmt = select(Delivery).where((Delivery.seller_email == me) | (Delivery.buyer_email == me))
    rows = db.execute(stmt).scalars().all()

    return [
        DeliveryOut(
            id=r.id,
            reservation_id=r.reservation_id,
            seller_email=r.seller_email,
            buyer_email=r.buyer_email,
            status=DeliveryStatus(r.status),
            carrier=r.carrier,
            notes=r.notes,
            created_at=r.created_at.isoformat().replace("+00:00", "Z"),
            updated_at=r.updated_at.isoformat().replace("+00:00", "Z"),
        )
        for r in rows
    ]


@router.get("/{delivery_id}", response_model=DeliveryOut)
def get_delivery(
    delivery_id: str,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    row = db.get(Delivery, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery not found")

    if me not in (row.seller_email, row.buyer_email):
        raise HTTPException(status_code=403, detail="Not allowed")

    return DeliveryOut(
        id=row.id,
        reservation_id=row.reservation_id,
        seller_email=row.seller_email,
        buyer_email=row.buyer_email,
        status=DeliveryStatus(row.status),
        carrier=row.carrier,
        notes=row.notes,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
        updated_at=row.updated_at.isoformat().replace("+00:00", "Z"),
    )


@router.patch("/{delivery_id}/status", response_model=DeliveryOut)
def update_status(
    delivery_id: str,
    payload: DeliveryUpdateStatus,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    row = db.get(Delivery, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery not found")

    # Only seller can update delivery status (MVP rule)
    if me != row.seller_email:
        raise HTTPException(status_code=403, detail="Not allowed")

    row.status = payload.status.value
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    db.commit()

    return DeliveryOut(
        id=row.id,
        reservation_id=row.reservation_id,
        seller_email=row.seller_email,
        buyer_email=row.buyer_email,
        status=DeliveryStatus(row.status),
        carrier=row.carrier,
        notes=row.notes,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
        updated_at=row.updated_at.isoformat().replace("+00:00", "Z"),
    )
