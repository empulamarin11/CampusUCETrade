from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol

@dataclass
class UserEntity:
    email: str
    password_hash: str

class UserRepository(Protocol):
    def get_by_email(self, email: str) -> Optional[UserEntity]: ...

class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, password_hash: str) -> bool: ...

class TokenService(Protocol):
    def create_access_token(self, subject: str) -> str: ...
    def verify_token(self, token: str) -> dict: ...