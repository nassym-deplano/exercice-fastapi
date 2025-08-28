from sqlalchemy import Column, String, UniqueConstraint, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.base import Base
import uuid


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Relations
    interventions = relationship("Intervention", back_populates="technician")

    # Contraintes d'unicité
    __table_args__ = (
        UniqueConstraint("email", "org", name="uq_technician_email_org"),
    )
