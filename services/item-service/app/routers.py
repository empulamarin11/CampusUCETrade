from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# In-memory store for MVP (later replace with PostgreSQL)
_ITEMS: Dict[str, dict] = {}

class ItemCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    price: float = Field(ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)

class ItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    price: Optional[float] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)

class ItemOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: float
    currency: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/", response_model=ItemOut)
def create_item(payload: ItemCreate):
    item_id = str(uuid4())
    item = {
        "id": item_id,
        "title": payload.title,
        "description": payload.description,
        "price": payload.price,
        "currency": payload.currency,
    }
    _ITEMS[item_id] = item
    return item

@router.get("/", response_model=List[ItemOut])
def list_items():
    return list(_ITEMS.values())

@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: str):
    item = _ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: str, payload: ItemUpdate):
    item = _ITEMS.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if payload.title is not None:
        item["title"] = payload.title
    if payload.description is not None:
        item["description"] = payload.description
    if payload.price is not None:
        item["price"] = payload.price
    if payload.currency is not None:
        item["currency"] = payload.currency

    _ITEMS[item_id] = item
    return item

@router.delete("/{item_id}")
def delete_item(item_id: str):
    if item_id not in _ITEMS:
        raise HTTPException(status_code=404, detail="Item not found")
    del _ITEMS[item_id]
    return {"deleted": True, "id": item_id}
