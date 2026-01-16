from __future__ import annotations
from dataclasses import dataclass
from app.domain.ports import UserRepository, PasswordHasher, UserEntity

def ensure_uce_email(email: str) -> None:
    if not email.lower().endswith("@uce.edu.ec"):
        raise ValueError("Email must be an institutional domain (@uce.edu.ec).")

@dataclass
class RegisterUser:
    repo: UserRepository
    hasher: PasswordHasher

    def execute(self, email: str, password: str, full_name: str | None = None) -> UserEntity:
        ensure_uce_email(email)

        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("User already exists.")

        pw_hash = self.hasher.hash(password)
        user = UserEntity(
            email=email,
            password_hash=pw_hash,
            full_name=full_name,
            role="student",
            is_active=True,
        )
        return self.repo.create(user)