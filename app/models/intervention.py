from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.base import Base
import uuid
import enum


class InterventionStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org = Column(String, nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    technician_id = Column(UUID(as_uuid=True), ForeignKey("technicians.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(InterventionStatus), default=InterventionStatus.PENDING, nullable=False)
    description = Column(String, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relations
    client = relationship("Client", back_populates="interventions")
    technician = relationship("Technician", back_populates="interventions")
    events = relationship("Event", back_populates="intervention")

    __table_args__ = (
        UniqueConstraint("client_id", "org", "description", name="uq_intervention_client_org_desc"),
    )
