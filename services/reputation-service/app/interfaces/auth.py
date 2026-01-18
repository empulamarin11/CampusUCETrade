# app/interfaces/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

from app.config import settings

security = HTTPBearer()


def get_current_email(creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(creds.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise ValueError("missing_sub")
        return str(sub).lower()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
