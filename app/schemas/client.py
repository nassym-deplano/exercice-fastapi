from pydantic import BaseModel, EmailStr, Field, constr
from typing import Annotated, Optional
from datetime import datetime
from uuid import UUID


class ClientBase(BaseModel):
    """Base model for client data."""

    name: Annotated[str, constr(min_length=1, max_length=100)] = Field(
        description="Nom complet du client", example="Jean Dupont"
    )
    email: EmailStr = Field(
        description="Adresse email du client", example="jean.dupont@email.com"
    )
    phone: Annotated[
        str, constr(min_length=6, max_length=20, pattern=r"^\+?\d{6,20}$")
    ] = Field(
        description="Numéro de téléphone du client (format international accepté)",
        example="+33123456789",
    )


class ClientRead(BaseModel):
    """Client data returned by the API."""

    id: UUID = Field(description="Identifiant unique du client")
    org: str = Field(description="Organisation du client")
    name: Annotated[str, constr(min_length=1, max_length=100)] = Field(
        description="Nom complet du client"
    )
    email: EmailStr = Field(description="Adresse email du client")
    phone: Annotated[
        str, constr(min_length=6, max_length=20, pattern=r"^\+?\d{6,20}$")
    ] = Field(description="Numéro de téléphone du client")
    deleted: bool = Field(description="Indique si le client est supprimé")
    created_at: datetime = Field(description="Date de création")
    updated_at: datetime = Field(description="Date de dernière modification")
    deleted_at: Optional[datetime] = Field(
        description="Date de suppression (si applicable)"
    )

    model_config = {"from_attributes": True}


class ClientCreate(BaseModel):
    """Data required to create a new client."""

    name: Annotated[str, constr(min_length=1, max_length=100)] = Field(
        ..., description="Nom complet du client", example="Jean Dupont"
    )
    email: EmailStr = Field(
        ...,
        description="Adresse email du client (doit être unique dans l'organisation)",
        example="jean.dupont@email.com",
    )
    phone: Annotated[
        str, constr(min_length=6, max_length=20, pattern=r"^\+?\d{6,20}$")
    ] = Field(
        ...,
        description="Numéro de téléphone du client",
        example="+33123456789",
    )


class ClientUpdate(BaseModel):
    """Data that can be updated for an existing client."""

    name: Annotated[Optional[str], constr(min_length=1, max_length=100)] = Field(
        None, description="Nom complet du client", example="Jean Dupont"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Adresse email du client (doit être unique dans l'organisation)",
        example="jean.dupont@email.com",
    )
    phone: Annotated[
        Optional[str], constr(min_length=6, max_length=20, pattern=r"^\+?\d{6,20}$")
    ] = Field(
        None,
        description="Numéro de téléphone du client (format international accepté)",
        example="+33123456789",
    )
