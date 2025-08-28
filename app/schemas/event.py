from pydantic import BaseModel, constr, Field
from typing import Annotated
from datetime import datetime
from uuid import UUID
from app.models.intervention import InterventionStatus
from app.models.event import EventType


class EventRead(BaseModel):
    """Event data returned by the API."""

    id: UUID = Field(description="Identifiant unique de l'événement")
    intervention_id: UUID = Field(description="Identifiant de l'intervention concernée")
    event_type: EventType = Field(description="Type d'événement")
    message: Annotated[str, constr(min_length=1)] = Field(
        description="Message descriptif de l'événement"
    )
    created_at: datetime = Field(description="Date de création de l'événement")

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    """Data required to create a new event."""

    intervention_id: UUID = Field(
        description="Identifiant de l'intervention concernée",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    event_type: EventType = Field(
        description="Type d'événement", example=EventType.STATUS_CHANGED
    )
    message: Annotated[str, constr(min_length=1)] | None = Field(
        default=None,
        description="Message descriptif de l'événement (optionnel)",
        example="Statut changé de PENDING vers IN_PROGRESS",
    )
    new_status: InterventionStatus | None = Field(
        default=None,
        description="Nouveau statut (pour les événements de changement de statut)",
        example=InterventionStatus.IN_PROGRESS,
    )
