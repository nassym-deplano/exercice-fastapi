from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID


class TechnicianRead(BaseModel):
    """Technician data returned by the API."""

    id: UUID = Field(description="Identifiant unique du technicien")
    org: str = Field(description="Organisation du technicien")
    name: Annotated[str, constr(min_length=1, max_length=100)] = Field(
        description="Nom complet du technicien"
    )
    email: EmailStr = Field(description="Adresse email du technicien")
    deleted: bool = Field(description="Indique si le technicien est supprimé")
    created_at: datetime = Field(description="Date de création")
    updated_at: datetime = Field(description="Date de dernière modification")

    model_config = {"from_attributes": True}


class TechnicianCreate(BaseModel):
    """Data required to create a new technician."""

    name: Annotated[str, constr(min_length=1, max_length=100)] = Field(
        ..., description="Nom complet du technicien", example="Pierre Martin"
    )
    email: EmailStr = Field(
        ...,
        description="Adresse email du technicien (doit être unique dans l'organisation)",
        example="pierre.martin@garage.com",
    )


class TechnicianUpdate(BaseModel):
    """Data that can be updated for an existing technician."""

    name: Annotated[str, constr(min_length=1, max_length=100)] | None = Field(
        None, description="Nom complet du technicien", example="Pierre Martin"
    )
    email: EmailStr | None = Field(
        None,
        description="Adresse email du technicien (doit être unique dans l'organisation)",
        example="pierre.martin@garage.com",
    )
