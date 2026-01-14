import os
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import TraceEvent

router = APIRouter(tags=["traceability"])

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


class TraceEventCreate(BaseModel):
    entity_type: str = Field(min_length=1, max_length=50)  # item, reservation, delivery, etc.
    entity_id: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=80)  # created, updated, etc.
    details: Optional[str] = Field(default=None, max_length=1000)


class TraceEventOut(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor_email: Optional[str] = None
    details: Optional[str] = None
    created_at: str


@router.get("/health")
def health():
    return {"status": "ok", "service": "traceability-service"}


@router.post("/events", response_model=TraceEventOut)
def create_event(
    payload: TraceEventCreate,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    event_id = str(uuid4())

    row = TraceEvent(
        id=event_id,
        entity_type=payload.entity_type.strip(),
        entity_id=payload.entity_id.strip(),
        action=payload.action.strip(),
        actor_email=me,
        details=payload.details,
        created_at=now,
    )
    db.add(row)
    db.commit()

    return TraceEventOut(
        id=row.id,
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        action=row.action,
        actor_email=row.actor_email,
        details=row.details,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )


@router.get("/events", response_model=List[TraceEventOut])
def list_events(
    entity_type: Optional[str] = Query(default=None),
    entity_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(TraceEvent).order_by(TraceEvent.created_at.desc())

    if entity_type:
        stmt = stmt.where(TraceEvent.entity_type == entity_type.strip())
    if entity_id:
        stmt = stmt.where(TraceEvent.entity_id == entity_id.strip())

    rows = db.execute(stmt).scalars().all()

    return [
        TraceEventOut(
            id=r.id,
            entity_type=r.entity_type,
            entity_id=r.entity_id,
            action=r.action,
            actor_email=r.actor_email,
            details=r.details,
            created_at=r.created_at.isoformat().replace("+00:00", "Z"),
        )
        for r in rows
    ]


@router.get("/events/{event_id}", response_model=TraceEventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    row = db.get(TraceEvent, event_id)
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")

    return TraceEventOut(
        id=row.id,
        entity_type=row.entity_type,
        entity_id=row.entity_id,
        action=row.action,
        actor_email=row.actor_email,
        details=row.details,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )
