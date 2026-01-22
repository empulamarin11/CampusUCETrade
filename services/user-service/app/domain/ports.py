from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol

@dataclass
class UserEntity:
    email: str
    password_hash: str
    full_name: str | None
    role: str
    is_active: bool

class UserRepository(Protocol):
    def get_by_email(self, email: str) -> Optional[UserEntity]: ...
    def create(self, user: UserEntity) -> UserEntity: ...

class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...