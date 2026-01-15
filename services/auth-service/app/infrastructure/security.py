import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

JWT_SECRET = os.getenv("JWT_SECRET", "dev_jwt_secret_key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptHasher:
    def hash(self, password: str) -> str:
        return _pwd.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        return _pwd.verify(password, password_hash)

class JwtService:
    def create_access_token(self, subject: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=JWT_EXPIRES_MIN)).timestamp()),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except JWTError as e:
            raise ValueError("Invalid token") from e
