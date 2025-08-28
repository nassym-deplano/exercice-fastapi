from datetime import datetime, UTC
from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.schemas.client import ClientCreate, ClientUpdate, ClientRead
from app.models.client import Client


class ClientService:

    @staticmethod
    def create_client(db: Session, data: ClientCreate, org: str) -> ClientRead:
        """
        Crée un nouveau client dans l'organisation spécifiée.
        Vérifie l'unicité de l'email avant la création.
        """
        existing = db.scalar(
            select(Client).where(
                Client.org == org,
                Client.email == data.email,
                Client.deleted == False,
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Client with this email already exists",
            )

        client = Client(**data.model_dump(), org=org)
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def list_clients(
        db: Session, org: str, limit: int = 50, offset: int = 0, q: str | None = None
    ) -> List[ClientRead]:
        """
        Récupère la liste des clients d'une organisation avec pagination et recherche.
        Permet de filtrer par nom ou email si un terme de recherche est fourni.
        """
        query = select(Client).where(Client.org == org, Client.deleted == False)
        if q:
            query = query.where(
                or_(Client.name.ilike(f"%{q}%"), Client.email.ilike(f"%{q}%"))
            )
        return db.scalars(query.limit(limit).offset(offset)).all()

    @staticmethod
    def get_client(db: Session, client_id: UUID, org: str) -> ClientRead:
        """
        Récupère un client spécifique par son ID dans l'organisation donnée.
        """
        client = db.scalar(
            select(Client).where(
                Client.id == client_id, Client.org == org, Client.deleted == False
            )
        )
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )
        return client

    @staticmethod
    def update_client(
        db: Session, client_id: UUID, data: ClientUpdate, org: str
    ) -> ClientRead:
        """
        Met à jour les informations d'un client existant.
        """
        client = ClientService.get_client(db, client_id, org)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(client, field, value)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def delete_client(db: Session, client_id: UUID, org: str):
        """
        Supprime logiquement un client en marquant le champ deleted à True.
        Le client n'est pas physiquement supprimé de la base de données.
        """
        client = ClientService.get_client(db, client_id, org)
        client.deleted = True
        client.deleted_at = datetime.now(UTC)
        db.commit()
