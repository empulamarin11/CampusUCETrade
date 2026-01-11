from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.db import Base


class TraceEvent(Base):
    __tablename__ = "trace_events"

    id = Column(String(36), primary_key=True)  # uuid string
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    action = Column(String(80), nullable=False)

    actor_email = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
