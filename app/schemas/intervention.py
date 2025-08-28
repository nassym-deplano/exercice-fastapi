from pydantic import BaseModel, constr, Field
from datetime import datetime
from typing import Annotated
from uuid import UUID
from app.models.intervention import InterventionStatus


class InterventionRead(BaseModel):
    """Intervention data returned by the API."""

    id: UUID = Field(description="Identifiant unique de l'intervention")
    org: str = Field(description="Organisation de l'intervention")
    client_id: UUID = Field(description="Identifiant du client")
    technician_id: UUID = Field(description="Identifiant du technicien assigné")
    status: InterventionStatus = Field(description="Statut actuel de l'intervention")
    description: Annotated[str, constr(min_length=1)] = Field(
        description="Description détaillée de l'intervention"
    )
    created_at: datetime = Field(description="Date de création")
    updated_at: datetime = Field(description="Date de dernière modification")
    deleted_at: datetime | None = Field(
        description="Date de suppression (si applicable)"
    )

    model_config = {"from_attributes": True}


class InterventionCreate(BaseModel):
    """Data required to create a new intervention."""

    client_id: UUID = Field(
        ...,
        description="Identifiant du client pour cette intervention",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    technician_id: UUID = Field(
        ...,
        description="Identifiant du technicien assigné à cette intervention",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    status: InterventionStatus = Field(
        description="Statut initial de l'intervention",
        example=InterventionStatus.PENDING,
    )
    description: Annotated[str, constr(min_length=1)] = Field(
        description="Description détaillée de l'intervention à effectuer",
        example="Réparation du système de freinage - remplacement des plaquettes",
    )


class InterventionUpdate(BaseModel):
    """Data that can be updated for an existing intervention."""

    technician_id: UUID | None = Field(
        default=None,
        description="Identifiant du technicien assigné (peut être modifié)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    status: InterventionStatus | None = Field(
        default=None,
        description="Nouveau statut de l'intervention (respecte les règles de transition)",
        example=InterventionStatus.IN_PROGRESS,
    )
    description: Annotated[str, constr(min_length=1)] | None = Field(
        default=None,
        description="Description mise à jour de l'intervention",
        example="Réparation du système de freinage - remplacement des plaquettes et vérification du liquide",
    )
