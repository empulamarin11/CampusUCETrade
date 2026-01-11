import os
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field, conint
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Rating

router = APIRouter(tags=["reputation"])

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


class RatingCreate(BaseModel):
    to_user_email: str = Field(min_length=5)
    score: conint(ge=1, le=5)  # 1..5
    comment: Optional[str] = Field(default=None, max_length=500)


class RatingOut(BaseModel):
    id: str
    from_user_email: str
    to_user_email: str
    score: int
    comment: Optional[str] = None
    created_at: str


@router.get("/health")
def health():
    return {"status": "ok", "service": "reputation-service"}


@router.post("/", response_model=RatingOut)
def create_rating(
    payload: RatingCreate,
    me: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    to_email = payload.to_user_email.strip().lower()
    if me == to_email:
        raise HTTPException(status_code=400, detail="You cannot rate yourself")

    now = datetime.now(timezone.utc)
    rating_id = str(uuid4())

    row = Rating(
        id=rating_id,
        from_user_email=me,
        to_user_email=to_email,
        score=int(payload.score),
        comment=payload.comment,
        created_at=now,
    )
    db.add(row)
    db.commit()

    return RatingOut(
        id=row.id,
        from_user_email=row.from_user_email,
        to_user_email=row.to_user_email,
        score=row.score,
        comment=row.comment,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )


@router.get("/", response_model=List[RatingOut])
def list_ratings(
    to_user_email: Optional[str] = Query(default=None, description="Filter by to_user_email"),
    db: Session = Depends(get_db),
):
    stmt = select(Rating).order_by(Rating.created_at.desc())
    if to_user_email:
        stmt = stmt.where(Rating.to_user_email == to_user_email.strip().lower())

    rows = db.execute(stmt).scalars().all()

    return [
        RatingOut(
            id=r.id,
            from_user_email=r.from_user_email,
            to_user_email=r.to_user_email,
            score=r.score,
            comment=r.comment,
            created_at=r.created_at.isoformat().replace("+00:00", "Z"),
        )
        for r in rows
    ]


@router.get("/{rating_id}", response_model=RatingOut)
def get_rating(rating_id: str, db: Session = Depends(get_db)):
    row = db.get(Rating, rating_id)
    if not row:
        raise HTTPException(status_code=404, detail="Rating not found")

    return RatingOut(
        id=row.id,
        from_user_email=row.from_user_email,
        to_user_email=row.to_user_email,
        score=row.score,
        comment=row.comment,
        created_at=row.created_at.isoformat().replace("+00:00", "Z"),
    )
