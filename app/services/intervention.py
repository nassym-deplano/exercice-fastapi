from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.schemas.intervention import (
    InterventionCreate,
    InterventionUpdate,
    InterventionRead,
)
from app.models.intervention import Intervention
from app.models.event import Event, EventType
from app.models.technician import Technician
from app.models.client import Client


class InterventionService:

    @staticmethod
    def create_item(
        db: Session, data: InterventionCreate, org: str
    ) -> InterventionRead:
        """
        Crée une nouvelle intervention pour un client.
        Vérifie l'existence du client et du technicien dans l'organisation.
        Assure l'unicité de la combinaison (client, description) dans l'organisation.
        Crée automatiquement un événement de création.
        """
        client = db.scalar(
            select(Client).where(
                Client.id == data.client_id, Client.org == org, Client.deleted == False
            )
        )
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found in this organization",
            )

        if data.technician_id is not None:
            tech = db.scalar(
                select(Technician).where(
                    Technician.id == data.technician_id,
                    Technician.org == org,
                    Technician.deleted == False,
                )
            )
            if not tech:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Technician not found in this organization",
                )

        existing = db.scalar(
            select(Intervention).where(
                Intervention.org == org,
                Intervention.client_id == data.client_id,
                Intervention.description == data.description,
                Intervention.deleted == False,
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An intervention with the same client and description already exists",
            )

        intervention = Intervention(**data.model_dump(), org=org)
        db.add(intervention)
        db.commit()
        db.refresh(intervention)

        created_event = Event(
            intervention_id=intervention.id,
            event_type=EventType.CREATED,
            message=f"Intervention created for client {client.name}",
        )
        db.add(created_event)
        db.commit()
        db.refresh(created_event)

        return intervention

    @staticmethod
    def list_items(
        db: Session,
        org: str,
        limit: int = 50,
        offset: int = 0,
        status_eq: Optional[str] = None,
        client_id: Optional[UUID] = None,
        q: Optional[str] = None,
    ) -> List[InterventionRead]:
        """
        Récupère la liste des interventions d'une organisation avec pagination et filtres.
        Permet de filtrer par statut, client ou rechercher dans la description.
        """
        query = select(Intervention).where(
            Intervention.org == org, Intervention.deleted == False
        )
        if status_eq:
            query = query.where(Intervention.status == status_eq)
        if client_id:
            query = query.where(Intervention.client_id == client_id)
        if q:
            query = query.where(Intervention.description.ilike(f"%{q}%"))
        return db.scalars(query.limit(limit).offset(offset)).all()

    @staticmethod
    def get_item(db: Session, item_id: UUID, org: str) -> InterventionRead:
        """
        Récupère une intervention spécifique par son ID dans l'organisation donnée.
        """
        intervention = db.scalar(
            select(Intervention).where(
                Intervention.id == item_id,
                Intervention.org == org,
                Intervention.deleted == False,
            )
        )
        if not intervention:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found"
            )
        return intervention

    @staticmethod
    def update_item(
        db: Session, item_id: UUID, data: InterventionUpdate, org: str
    ) -> InterventionRead:
        """
        Met à jour une intervention existante.
        Valide les transitions de statut autorisées et crée un événement de changement de statut si nécessaire.
        """
        intervention = InterventionService.get_item(db, item_id, org)

        old_status = intervention.status

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(intervention, field, value)

        new_status = getattr(intervention, "status", None)
        if new_status and new_status != old_status:
            allowed_transitions = {
                "PENDING": ["IN_PROGRESS"],
                "IN_PROGRESS": ["COMPLETED", "CANCELLED"],
                "COMPLETED": [],
                "CANCELLED": [],
            }

            if new_status.value not in allowed_transitions[old_status.value]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Invalid status transition from {old_status.value} to {new_status.value}",
                )

            event = Event(
                intervention_id=intervention.id,
                event_type=EventType.STATUS_CHANGED,
                message=f"Status changed from {old_status.value} to {new_status.value}",
            )
            db.add(event)

        db.commit()
        db.refresh(intervention)
        return intervention

    @staticmethod
    def delete_item(db: Session, item_id: UUID, org: str):
        """
        Supprime logiquement une intervention en marquant le champ deleted à True.
        L'intervention n'est pas physiquement supprimée de la base de données.
        """
        intervention = InterventionService.get_item(db, item_id, org)
        intervention.deleted = True
        intervention.deleted_at = datetime.now(UTC)
        db.commit()
