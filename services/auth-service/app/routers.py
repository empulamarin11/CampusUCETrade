from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import APIRouter, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["auth"])
# Use pbkdf2_sha256 for maximum compatibility in slim containers (no native deps)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
# In-memory store for demo (will move to Postgres later)
_USERS: Dict[str, str] = {}

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"
ACCESS_TOKEN_MINUTES = 60


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.get("/health")
async def health():
    return {"status": "ok", "service": "auth-service"}


@router.post("/register")
async def register(payload: RegisterIn):
    if payload.email in _USERS:
        raise HTTPException(status_code=409, detail="User already exists")

    _USERS[payload.email] = pwd_context.hash(payload.password)
    return {"created": True, "email": payload.email}


@router.post("/token", response_model=TokenOut)
async def token(payload: RegisterIn):
    hashed = _USERS.get(payload.email)
    if not hashed or not pwd_context.verify(payload.password, hashed):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    claims = {"sub": payload.email, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}

    token_str = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)
    return TokenOut(access_token=token_str)
