from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, conint

router = APIRouter()

# In-memory store for MVP (later replace with PostgreSQL)
_RATINGS: Dict[str, dict] = {}

class RatingCreate(BaseModel):
    from_user_id: str = Field(min_length=1)
    to_user_id: str = Field(min_length=1)
    score: conint(ge=1, le=5)  # 1..5
    comment: Optional[str] = Field(default=None, max_length=500)

class RatingOut(BaseModel):
    id: str
    from_user_id: str
    to_user_id: str
    score: int
    comment: Optional[str] = None
    created_at: str

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/", response_model=RatingOut)
def create_rating(payload: RatingCreate):
    rating_id = str(uuid4())
    rating = {
        "id": rating_id,
        "from_user_id": payload.from_user_id,
        "to_user_id": payload.to_user_id,
        "score": int(payload.score),
        "comment": payload.comment,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _RATINGS[rating_id] = rating
    return rating

@router.get("/", response_model=List[RatingOut])
def list_ratings(
    to_user_id: Optional[str] = Query(default=None, description="Filter by to_user_id"),
):
    items = list(_RATINGS.values())
    if to_user_id:
        items = [r for r in items if r["to_user_id"] == to_user_id]
    return items

@router.get("/{rating_id}", response_model=RatingOut)
def get_rating(rating_id: str):
    rating = _RATINGS.get(rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating
