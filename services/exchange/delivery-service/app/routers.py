from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store for MVP (later replace with PostgreSQL + S3 evidence)
_DELIVERIES: Dict[str, dict] = {}

class DeliveryStatus(str, Enum):
    created = "created"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"

class DeliveryCreate(BaseModel):
    reservation_id: str = Field(min_length=1)
    carrier: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=500)

class DeliveryOut(BaseModel):
    id: str
    reservation_id: str
    status: DeliveryStatus
    carrier: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

class DeliveryUpdateStatus(BaseModel):
    status: DeliveryStatus

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/", response_model=DeliveryOut)
def create_delivery(payload: DeliveryCreate):
    delivery_id = str(uuid4())
    now = datetime.utcnow().isoformat() + "Z"
    delivery = {
        "id": delivery_id,
        "reservation_id": payload.reservation_id,
        "status": DeliveryStatus.created,
        "carrier": payload.carrier,
        "notes": payload.notes,
        "created_at": now,
        "updated_at": now,
    }
    _DELIVERIES[delivery_id] = delivery
    return delivery

@router.get("/", response_model=List[DeliveryOut])
def list_deliveries():
    return list(_DELIVERIES.values())

@router.get("/{delivery_id}", response_model=DeliveryOut)
def get_delivery(delivery_id: str):
    delivery = _DELIVERIES.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return delivery

@router.patch("/{delivery_id}/status", response_model=DeliveryOut)
def update_status(delivery_id: str, payload: DeliveryUpdateStatus):
    delivery = _DELIVERIES.get(delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    delivery["status"] = payload.status
    delivery["updated_at"] = datetime.utcnow().isoformat() + "Z"
    _DELIVERIES[delivery_id] = delivery
    return delivery
