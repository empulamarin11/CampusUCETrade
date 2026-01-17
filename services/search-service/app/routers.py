from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Item
from app.s3 import presign_get

router = APIRouter()


class SearchResult(BaseModel):
    id: str
    title: str
    price: float
    currency: str
    media_key: str | None = None
    media_url: str | None = None


@router.get("/health")
def health():
    return {"status": "ok", "service": "search-service"}


@router.get("/", response_model=List[SearchResult])
def search(
    q: Optional[str] = Query(default=None, description="Search query"),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    filters = []
    if q:
        filters.append(Item.title.ilike(f"%{q}%"))
    if min_price is not None:
        filters.append(Item.price >= min_price)
    if max_price is not None:
        filters.append(Item.price <= max_price)

    query_db = db.query(Item)
    if filters:
        query_db = query_db.filter(and_(*filters))

    rows = query_db.order_by(Item.created_at.desc()).limit(limit).all()

    results: List[SearchResult] = []
    for r in rows:
        media_url = None
        if getattr(r, "media_key", None):
            # Presigned GET (works for MinIO local + AWS later)
            media_url = presign_get(r.media_key, expires_in=900)

        results.append(
            SearchResult(
                id=r.id,
                title=r.title,
                price=float(r.price),
                currency=r.currency,
                media_key=getattr(r, "media_key", None),
                media_url=media_url,
            )
        )

    return results