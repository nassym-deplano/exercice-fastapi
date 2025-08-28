from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.base import Base
import uuid
import enum


class EventType(enum.Enum):
    CREATED = "CREATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    NOTE = "NOTE"


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    # Relations
    intervention = relationship("Intervention", back_populates="events")

    # Index pour optimiser les requêtes par intervention et date
    __table_args__ = (
        Index("idx_events_intervention_created", "intervention_id", "created_at"),
    )
