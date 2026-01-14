from datetime import datetime
from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)

    reservation_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    seller_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    buyer_email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False)  # created/in_transit/delivered/failed

    carrier: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
