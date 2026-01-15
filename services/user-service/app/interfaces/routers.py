from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.infrastructure.db import get_db
from app.infrastructure.repositories import SqlAlchemyUserRepository
from app.infrastructure.security import BcryptHasher
from app.application.use_cases import RegisterUser

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/users/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    repo = SqlAlchemyUserRepository(db)
    hasher = BcryptHasher()
    uc = RegisterUser(repo=repo, hasher=hasher)

    try:
        user = uc.execute(email=payload.email, password=payload.password, full_name=payload.full_name)
        return {"email": user.email, "full_name": user.full_name, "role": user.role, "is_active": user.is_active}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))