from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store for MVP (later replace with PostgreSQL)
_EVENTS: Dict[str, dict] = {}

class TraceEventCreate(BaseModel):
    entity_type: str = Field(min_length=1, max_length=50)  # e.g., "item", "reservation"
    entity_id: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=80)       # e.g., "created", "updated"
    actor_user_id: Optional[str] = Field(default=None, max_length=100)
    details: Optional[str] = Field(default=None, max_length=1000)

class TraceEventOut(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor_user_id: Optional[str] = None
    details: Optional[str] = None
    created_at: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/events", response_model=TraceEventOut)
def create_event(payload: TraceEventCreate):
    event_id = str(uuid4())
    event = {
        "id": event_id,
        "entity_type": payload.entity_type,
        "entity_id": payload.entity_id,
        "action": payload.action,
        "actor_user_id": payload.actor_user_id,
        "details": payload.details,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _EVENTS[event_id] = event
    return event

@router.get("/events", response_model=List[TraceEventOut])
def list_events(
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[str] = Query(default=None),
):
    items = list(_EVENTS.values())

    if entity_type:
        items = [e for e in items if e["entity_type"] == entity_type]
    if entity_id:
        items = [e for e in items if e["entity_id"] == entity_id]

    return items

