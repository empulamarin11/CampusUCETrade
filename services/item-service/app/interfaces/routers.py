import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.infrastructure.s3 import presign_get, presign_put


from app.infrastructure.db import get_db
from app.infrastructure.models import Item

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")

security = HTTPBearer()


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
    owner_email: str
    title: str
    description: Optional[str] = None
    price: float
    currency: str
    media_key: Optional[str] = None
    media_content_type: Optional[str] = None

class MediaPresignOut(BaseModel):
    object_key: str
    upload_url: str
    download_url: str
    expires_in: int


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


@router.get("/health")
def health():
    return {"status": "ok", "service": "item-service"}


@router.post("/", response_model=ItemOut)
def create_item(payload: ItemCreate, email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    item_id = str(uuid4())

    item = Item(
        id=item_id,
        owner_email=email,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        currency=payload.currency,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(item)
    db.commit()

    return ItemOut(
        id=item.id,
        owner_email=item.owner_email,
        title=item.title,
        description=item.description,
        price=float(item.price),
        currency=item.currency,
    )


@router.get("/", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    rows = db.query(Item).order_by(Item.created_at.desc()).all()
    return [
        ItemOut(
            id=r.id,
            owner_email=r.owner_email,
            title=r.title,
            description=r.description,
            price=float(r.price),
            currency=r.currency,
        )
        for r in rows
    ]


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: str, db: Session = Depends(get_db)):
    r = db.get(Item, item_id)
    if not r:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemOut(
        id=r.id,
        owner_email=r.owner_email,
        title=r.title,
        description=r.description,
        price=float(r.price),
        currency=r.currency,
    )


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: str, payload: ItemUpdate, email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    r = db.get(Item, item_id)
    if not r:
        raise HTTPException(status_code=404, detail="Item not found")
    if r.owner_email != email:
        raise HTTPException(status_code=403, detail="Not allowed")

    if payload.title is not None:
        r.title = payload.title
    if payload.description is not None:
        r.description = payload.description
    if payload.price is not None:
        r.price = payload.price
    if payload.currency is not None:
        r.currency = payload.currency

    r.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(r)

    return ItemOut(
        id=r.id,
        owner_email=r.owner_email,
        title=r.title,
        description=r.description,
        price=float(r.price),
        currency=r.currency,
    )


@router.delete("/{item_id}")
def delete_item(item_id: str, email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    r = db.get(Item, item_id)
    if not r:
        raise HTTPException(status_code=404, detail="Item not found")
    if r.owner_email != email:
        raise HTTPException(status_code=403, detail="Not allowed")

    db.delete(r)
    db.commit()
    return {"deleted": True, "id": item_id}

def _ext_from_content_type(ct: str) -> str:
    ct = ct.lower().strip()
    if ct == "image/jpeg":
        return "jpg"
    if ct == "image/png":
        return "png"
    if ct == "image/webp":
        return "webp"
    raise HTTPException(status_code=400, detail="Only image/jpeg, image/png, image/webp allowed")


@router.post("/{item_id}/media/presign", response_model=MediaPresignOut)
def presign_item_media(
    item_id: str,
    content_type: str = Query(..., description="image/jpeg | image/png | image/webp"),
    email: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_email != email:
        raise HTTPException(status_code=403, detail="Not allowed")

    ext = _ext_from_content_type(content_type)
    key = f"items/{item_id}/{uuid4()}.{ext}"

    expires = 900
    upload_url = presign_put(key=key, content_type=content_type, expires_in=expires)
    download_url = presign_get(key=key, expires_in=expires)

    item.media_key = key
    item.media_content_type = content_type
    item.updated_at = datetime.utcnow()
    db.add(item)
    db.commit()

    return MediaPresignOut(
        object_key=key,
        upload_url=upload_url,
        download_url=download_url,
        expires_in=expires,
    )