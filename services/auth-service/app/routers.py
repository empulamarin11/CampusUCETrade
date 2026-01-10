import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

router = APIRouter(tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
ALLOWED_EMAIL_DOMAIN = os.getenv("ALLOWED_EMAIL_DOMAIN", "@uce.edu.ec").lower()

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class TokenIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _enforce_uce_email(email: str) -> None:
    e = email.strip().lower()
    if not e.endswith(ALLOWED_EMAIL_DOMAIN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only institutional emails are allowed ({ALLOWED_EMAIL_DOMAIN}).",
        )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "auth-service"}


@router.post(
    "/token",
    response_model=TokenOut,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def token(payload: TokenIn, db: Session = Depends(get_db)):
    _enforce_uce_email(payload.email)

    email = payload.email.strip().lower()
    user = db.get(User, email)

    if not user or not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    claims = {"sub": email, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}

    token_str = jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALG)
    return TokenOut(access_token=token_str)
