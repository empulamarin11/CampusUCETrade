from __future__ import annotations
from dataclasses import dataclass
from app.domain.ports import UserRepository, PasswordHasher, TokenService

def ensure_uce_email(email: str) -> None:
    if not email.lower().endswith("@uce.edu.ec"):
        raise ValueError("Email must be an institutional domain (@uce.edu.ec).")

@dataclass
class LoginUser:
    repo: UserRepository
    hasher: PasswordHasher
    tokens: TokenService

    def execute(self, email: str, password: str) -> str:
        ensure_uce_email(email)
        user = self.repo.get_by_email(email)
        if not user or not self.hasher.verify(password, user.password_hash):
            raise ValueError("Invalid credentials.")
        return self.tokens.create_access_token(subject=user.email)

@dataclass
class ValidateToken:
    tokens: TokenService

    def execute(self, token: str) -> dict:
        return self.tokens.verify_token(token)