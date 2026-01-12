import os
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Reservation
from app.mq import publish_event

router = APIRouter(tags=["reservations"])

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
        return str(email).strip().lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class ReservationCreate(BaseModel):
    item_id: str = Field(min_length=1, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)


class ReservationOut(BaseModel):
    id: str
    item_id: str
    requester_email: str
    status: ReservationStatus
    notes: Optional[str] = None
    created_at: str


class ReservationUpdateStatus(BaseModel):
    status: ReservationStatus


@router.get("/health")
def health():
    return {"status": "ok", "service": "reservation-service"}


@router.post("/", response_model=ReservationOut)
def create_reservation(
    payload: ReservationCreate,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    reservation_id = str(uuid4())

    row = Reservation(
        id=reservation_id,
        item_id=payload.item_id,
        requester_email=me,
        status=ReservationStatus.pending.value,
        notes=payload.notes,
        created_at=now,
    )

    db.add(row)
    db.commit()

    # Publish event (non-fatal if Rabbit is down)
    publish_event(
        "reservation.created",
        {
            "type": "reservation.created",
            "reservation_id": row.id,
            "item_id": row.item_id,
            "requester_email": row.requester_email,
            "status": row.status,
            "notes": row.notes,
            "ts": now.isoformat().replace("+00:00", "Z"),
        },
    )

    return ReservationOut(
        id=row.id,
        item_id=row.item_id,
        requester_email=row.requester_email,
        status=ReservationStatus(row.status),
        notes=row.notes,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )


@router.get("/", response_model=List[ReservationOut])
def list_reservations(
    me: str = Depends(get_current_email),
    status: Optional[ReservationStatus] = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Reservation).where(Reservation.requester_email == me).order_by(Reservation.created_at.desc())
    if status:
        stmt = stmt.where(Reservation.status == status.value)

    rows = db.execute(stmt).scalars().all()

    return [
        ReservationOut(
            id=r.id,
            item_id=r.item_id,
            requester_email=r.requester_email,
            status=ReservationStatus(r.status),
            notes=r.notes,
            created_at=r.created_at.isoformat().replace("+00:00", "Z"),
        )
        for r in rows
    ]


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(
    reservation_id: str,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    row = db.get(Reservation, reservation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if row.requester_email != me:
        raise HTTPException(status_code=403, detail="Not allowed")

    return ReservationOut(
        id=row.id,
        item_id=row.item_id,
        requester_email=row.requester_email,
        status=ReservationStatus(row.status),
        notes=row.notes,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )


@router.patch("/{reservation_id}/status", response_model=ReservationOut)
def update_status(
    reservation_id: str,
    payload: ReservationUpdateStatus,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    row = db.get(Reservation, reservation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if row.requester_email != me:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Simple rules for MVP
    # - requester can cancel or (optionally) confirm their reservation
    if payload.status not in [ReservationStatus.cancelled, ReservationStatus.confirmed, ReservationStatus.pending]:
        raise HTTPException(status_code=400, detail="Invalid status")

    row.status = payload.status.value
    db.add(row)
    db.commit()

    now = datetime.now(timezone.utc)

    publish_event(
        f"reservation.{row.status}",
        {
            "type": f"reservation.{row.status}",
            "reservation_id": row.id,
            "item_id": row.item_id,
            "requester_email": row.requester_email,
            "status": row.status,
            "notes": row.notes,
            "ts": now.isoformat().replace("+00:00", "Z"),
        },
    )

    return ReservationOut(
        id=row.id,
        item_id=row.item_id,
        requester_email=row.requester_email,
        status=ReservationStatus(row.status),
        notes=row.notes,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )
