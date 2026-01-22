import os
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Notification

router = APIRouter(tags=["notifications"])

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


class NotificationCreate(BaseModel):
    # This must match the authenticated user
    user_email: str = Field(min_length=5)
    title: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=1000)
    type: str = Field(default="info", max_length=30)


class NotificationOut(BaseModel):
    id: str
    user_email: str
    title: str
    message: str
    type: str
    created_at: str
    read: bool


@router.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}


@router.post("/", response_model=NotificationOut)
def create_notification(
    payload: NotificationCreate,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    if me != payload.user_email.lower():
        raise HTTPException(status_code=403, detail="Not allowed")

    now = datetime.now(timezone.utc)
    notif_id = str(uuid4())

    row = Notification(
        id=notif_id,
        user_email=me,
        title=payload.title,
        message=payload.message,
        type=payload.type,
        created_at=now,
        read=False,
    )
    db.add(row)
    db.commit()

    return NotificationOut(
        id=row.id,
        user_email=row.user_email,
        title=row.title,
        message=row.message,
        type=row.type,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
        read=bool(row.read),
    )


@router.get("/", response_model=List[NotificationOut])
def list_notifications(
    unread_only: bool = Query(default=False),
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    stmt = select(Notification).where(Notification.user_email == me)
    if unread_only:
        stmt = stmt.where(Notification.read.is_(False))

    stmt = stmt.order_by(Notification.created_at.desc())
    rows = db.execute(stmt).scalars().all()

    return [
        NotificationOut(
            id=r.id,
            user_email=r.user_email,
            title=r.title,
            message=r.message,
            type=r.type,
            created_at=r.created_at.isoformat().replace("+00:00", "Z"),
            read=bool(r.read),
        )
        for r in rows
    ]


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: str,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    row = db.get(Notification, notification_id)
    if not row:
        raise HTTPException(status_code=404, detail="Notification not found")

    if row.user_email != me:
        raise HTTPException(status_code=403, detail="Not allowed")

    row.read = True
    db.add(row)
    db.commit()

    return NotificationOut(
        id=row.id,
        user_email=row.user_email,
        title=row.title,
        message=row.message,
        type=row.type,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
        read=bool(row.read),
    )
