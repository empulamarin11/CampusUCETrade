# app/routers.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import AuditEvent

router = APIRouter()
security = HTTPBearer()


def _current_email(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("missing_sub")
        return str(sub).lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/health")
def health():
    return {"status": "ok", "service": "traceability-service", "protocol": "kafka"}

@router.post("/audit/seed")
def seed_audit(
    db: Session = Depends(get_db),
    _email: str = Depends(_current_email),
):
    row = AuditEvent(
        event_type="test.event",
        source="manual",
        payload_json='{"hello":"world"}',
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"ok": True, "id": str(row.id)}


@router.get("/audit")
def list_audit(
    limit: int = 50,
    db: Session = Depends(get_db),
    _email: str = Depends(_current_email),
):
    limit = max(1, min(limit, 200))
    rows = (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(r.id),
            "event_type": r.event_type,
            "source": r.source,
            "payload_json": r.payload_json,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
