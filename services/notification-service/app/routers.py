from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store for MVP (later replace with PostgreSQL + message broker)
_NOTIFICATIONS: Dict[str, dict] = {}

class NotificationCreate(BaseModel):
    user_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=1000)
    type: str = Field(default="info", max_length=30)

class NotificationOut(BaseModel):
    id: str
    user_id: str
    title: str
    message: str
    type: str
    created_at: str
    read: bool

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/", response_model=NotificationOut)
def create_notification(payload: NotificationCreate):
    notif_id = str(uuid4())
    notif = {
        "id": notif_id,
        "user_id": payload.user_id,
        "title": payload.title,
        "message": payload.message,
        "type": payload.type,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "read": False,
    }
    _NOTIFICATIONS[notif_id] = notif
    return notif

@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    user_id: Optional[str] = Query(default=None, description="Filter by user_id"),
    unread_only: bool = Query(default=False, description="Return only unread notifications"),
):
    items = list(_NOTIFICATIONS.values())

    if user_id:
        items = [n for n in items if n["user_id"] == user_id]

    if unread_only:
        items = [n for n in items if n["read"] is False]

    return items

@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: str):
    notif = _NOTIFICATIONS.get(notification_id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif["read"] = True
    _NOTIFICATIONS[notification_id] = notif
    return notif
