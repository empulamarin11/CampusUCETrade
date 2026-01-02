from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store for MVP (later replace with PostgreSQL)
_RESERVATIONS: Dict[str, dict] = {}

class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class ReservationCreate(BaseModel):
    item_id: str = Field(min_length=1)
    requester_user_id: str = Field(min_length=1)
    notes: Optional[str] = Field(default=None, max_length=500)

class ReservationOut(BaseModel):
    id: str
    item_id: str
    requester_user_id: str
    status: ReservationStatus
    notes: Optional[str] = None
    created_at: str

class ReservationUpdateStatus(BaseModel):
    status: ReservationStatus

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/", response_model=ReservationOut)
def create_reservation(payload: ReservationCreate):
    reservation_id = str(uuid4())
    reservation = {
        "id": reservation_id,
        "item_id": payload.item_id,
        "requester_user_id": payload.requester_user_id,
        "status": ReservationStatus.pending,
        "notes": payload.notes,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _RESERVATIONS[reservation_id] = reservation
    return reservation

@router.get("/", response_model=List[ReservationOut])
def list_reservations():
    return list(_RESERVATIONS.values())

@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: str):
    reservation = _RESERVATIONS.get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.patch("/{reservation_id}/status", response_model=ReservationOut)
def update_status(reservation_id: str, payload: ReservationUpdateStatus):
    reservation = _RESERVATIONS.get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    reservation["status"] = payload.status
    _RESERVATIONS[reservation_id] = reservation
    return reservation
