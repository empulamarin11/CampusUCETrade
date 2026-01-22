from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session

from app.domain.ports import UserEntity
from app.infrastructure.models import User

class SqlAlchemyUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        u = self.db.query(User).filter(User.email == email).first()
        if not u:
            return None
        return UserEntity(email=u.email, password_hash=u.password_hash)