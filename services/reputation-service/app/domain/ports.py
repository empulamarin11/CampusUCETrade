# app/domain/ports.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional
from app.domain.models import Reputation


@dataclass(frozen=True)
class RatingInput:
    user_email: str
    points: int  # 1..5 (MVP)


class ReputationRepositoryPort(Protocol):
    def get_by_email(self, user_email: str) -> Optional[Reputation]:
        ...

    def save(self, rep: Reputation) -> Reputation:
        ...


class ScoringRulePort(Protocol):
    """Open/Closed: you can add new rules without changing the flow."""
    def apply(self, current_score: int, rating: RatingInput) -> int:
        ...
