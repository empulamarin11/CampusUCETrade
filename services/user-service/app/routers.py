# services/user-service/app/routers.py

import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

router = APIRouter(tags=["users"])

# JWT (shared with auth-service via env vars)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")

# Email policy
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "@uce.edu.ec").lower()

# Password hashing (compatible with slim containers)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Swagger "Authorize" button (Bearer token)
security = HTTPBearer()


# ---------- Schemas ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class RegisterOut(BaseModel):
    created: bool
    email: EmailStr


class ProfileOut(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "student"
    is_active: bool = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None


# ---------- Auth helpers ----------
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


# ---------- Routes ----------
@router.get("/health")
async def health():
    return {"status": "ok", "service": "user-service"}


@router.post("/register", response_model=RegisterOut)
async def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()

    if not email.endswith(ALLOWED_EMAIL_DOMAIN):
        raise HTTPException(
            status_code=400,
            detail=f"Only institutional emails are allowed ({ALLOWED_EMAIL_DOMAIN}).",
        )

    exists = db.get(User, email)
    if exists:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=email,
        password_hash=pwd_context.hash(payload.password),
        full_name=payload.full_name,
        role="student",
        is_active=True,
    )
    db.add(user)
    db.commit()

    return RegisterOut(created=True, email=email)


@router.get("/me", response_model=ProfileOut)
async def me(email: str = Depends(get_current_email), db: Session = Depends(get_db)):
    user = db.get(User, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return ProfileOut(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )


@router.put("/me", response_model=ProfileOut)
async def update_me(
    payload: ProfileUpdate,
    email: str = Depends(get_current_email),
    db: Session = Depends(get_db),
):
    user = db.get(User, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name is not None:
        user.full_name = payload.full_name

    db.commit()
    db.refresh(user)

    return ProfileOut(
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
    )
