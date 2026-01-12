from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

# Mock dataset for MVP (later replace with PostgreSQL / full-text search)
_MOCK_ITEMS = [
    {"id": "1", "title": "Laptop Dell", "price": 350.0, "currency": "USD"},
    {"id": "2", "title": "Calculadora Cientifica", "price": 15.0, "currency": "USD"},
    {"id": "3", "title": "Libro de Programacion", "price": 8.0, "currency": "USD"},
]

class SearchResult(BaseModel):
    id: str
    title: str
    price: float
    currency: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/", response_model=List[SearchResult])
def search(
    q: Optional[str] = Query(default=None, description="Search query"),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
):
    results = _MOCK_ITEMS

    if q:
        q_lower = q.lower()
        results = [x for x in results if q_lower in x["title"].lower()]

    if min_price is not None:
        results = [x for x in results if x["price"] >= min_price]

    if max_price is not None:
        results = [x for x in results if x["price"] <= max_price]

    return results
