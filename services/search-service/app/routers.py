from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Item

router = APIRouter()


class SearchResult(BaseModel):
    id: str
    title: str
    price: float
    currency: str


@router.get("/health")
def health():
    return {"status": "ok", "service": "search-service"}


@router.get("/", response_model=List[SearchResult])
def search(
    q: Optional[str] = Query(default=None, description="Search query"),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    db: Session = Depends(get_db),
):
    filters = []
    if q:
        filters.append(Item.title.ilike(f"%{q}%"))
    if min_price is not None:
        filters.append(Item.price >= min_price)
    if max_price is not None:
        filters.append(Item.price <= max_price)

    query = db.query(Item)
    if filters:
        query = query.filter(and_(*filters))

    rows = query.order_by(Item.created_at.desc()).limit(50).all()

    return [
        SearchResult(
            id=r.id,
            title=r.title,
            price=float(r.price),
            currency=r.currency,
        )
        for r in rows
    ]
