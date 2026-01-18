# app/application/dtos.py
from pydantic import BaseModel, Field


class RateUserIn(BaseModel):
    user_email: str
    points: int = Field(ge=1, le=5)
    feedback: str | None = None  # MVP (no persistimos aún)


class ReputationOut(BaseModel):
    user_email: str
    score: int
    ratings_count: int
