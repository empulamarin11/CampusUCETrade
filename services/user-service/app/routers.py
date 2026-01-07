from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["users"])

# In-memory store for demo (will move to Postgres later)
_PROFILES: Dict[str, dict] = {}

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"

# This enables Swagger "Authorize" button for Bearer tokens
security = HTTPBearer()


class ProfileOut(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "student"
    is_active: bool = True


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None


def get_current_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    # Swagger will send: Authorization: Bearer <token>
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token missing subject")
        return email
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/health")
async def health():
    return {"status": "ok", "service": "user-service"}


@router.get("/me", response_model=ProfileOut)
async def me(email: str = Depends(get_current_email)):
    profile = _PROFILES.get(email)
    if not profile:
        profile = {"email": email, "full_name": None, "role": "student", "is_active": True}
        _PROFILES[email] = profile
    return profile


@router.put("/me", response_model=ProfileOut)
async def update_me(payload: ProfileUpdate, email: str = Depends(get_current_email)):
    profile = _PROFILES.get(email) or {"email": email, "full_name": None, "role": "student", "is_active": True}
    if payload.full_name is not None:
        profile["full_name"] = payload.full_name
    _PROFILES[email] = profile
    return profile
