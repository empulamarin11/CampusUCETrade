# app/domain/models.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Reputation(Base):
    __tablename__ = "reputations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0..100 (MVP)

    ratings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
