from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from app.infrastructure.db import get_db
from app.infrastructure.repositories import SqlAlchemyUserRepository
from app.infrastructure.security import BcryptHasher, JwtService
from app.application.use_cases import LoginUser, ValidateToken

router = APIRouter()

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ValidateOut(BaseModel):
    valid: bool
    payload: dict

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/auth/login", response_model=TokenOut, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def login(payload: LoginIn, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    hasher = BcryptHasher()
    tokens = JwtService()
    uc = LoginUser(repo=repo, hasher=hasher, tokens=tokens)
    try:
        token = uc.execute(email=payload.email, password=payload.password)
        return TokenOut(access_token=token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/auth/validate", response_model=ValidateOut)
def validate(token: str):
    uc = ValidateToken(tokens=JwtService())
    try:
        payload = uc.execute(token=token)
        return ValidateOut(valid=True, payload=payload)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))