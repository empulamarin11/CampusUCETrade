import os
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Reservation

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
security = HTTPBearer()


class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class ReservationCreate(BaseModel):
    item_id: str = Field(min_length=1)
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


@router.get("/health")
def health():
    return {"status": "ok", "service": "reservation-service"}


@router.post("/", response_model=ReservationOut)
def create_reservation(payload: ReservationCreate, email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    reservation_id = str(uuid4())
    r = Reservation(
        id=reservation_id,
        item_id=payload.item_id,
        requester_email=email,
        status=ReservationStatus.pending.value,
        notes=payload.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(r)
    db.commit()

    return ReservationOut(
        id=r.id,
        item_id=r.item_id,
        requester_email=r.requester_email,
        status=ReservationStatus(r.status),
        notes=r.notes,
        created_at=r.created_at.isoformat() + "Z",
    )


@router.get("/", response_model=List[ReservationOut])
def list_my_reservations(email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    rows = (
        db.query(Reservation)
        .filter(Reservation.requester_email == email)
        .order_by(Reservation.created_at.desc())
        .all()
    )
    return [
        ReservationOut(
            id=r.id,
            item_id=r.item_id,
            requester_email=r.requester_email,
            status=ReservationStatus(r.status),
            notes=r.notes,
            created_at=r.created_at.isoformat() + "Z",
        )
        for r in rows
    ]


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: str, email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if r.requester_email != email:
        raise HTTPException(status_code=403, detail="Not allowed")

    return ReservationOut(
        id=r.id,
        item_id=r.item_id,
        requester_email=r.requester_email,
        status=ReservationStatus(r.status),
        notes=r.notes,
        created_at=r.created_at.isoformat() + "Z",
    )


@router.patch("/{reservation_id}/status", response_model=ReservationOut)
def update_status(reservation_id: str, payload: ReservationUpdateStatus, email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    r = db.get(Reservation, reservation_id)
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if r.requester_email != email:
        raise HTTPException(status_code=403, detail="Not allowed")

    # For now requester can only cancel their own reservation.
    if payload.status != ReservationStatus.cancelled:
        raise HTTPException(status_code=400, detail="Only cancellation is allowed by requester")

    r.status = payload.status.value
    r.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(r)

    return ReservationOut(
        id=r.id,
        item_id=r.item_id,
        requester_email=r.requester_email,
        status=ReservationStatus(r.status),
        notes=r.notes,
        created_at=r.created_at.isoformat() + "Z",
    )
