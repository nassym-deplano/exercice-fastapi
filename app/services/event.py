from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.intervention import Intervention, InterventionStatus
from app.models.event import Event, EventType
from app.schemas.event import EventCreate


class EventService:

    @staticmethod
    def create_event(db: Session, data: EventCreate, org: str):
        """
        Crée un nouvel événement pour une intervention.
        Gère différents types d'événements (création, changement de statut, commentaires).
        Valide les transitions de statut autorisées.
        """
        intervention = (
            db.query(Intervention)
            .filter(
                Intervention.id == data.intervention_id,
                Intervention.org == org,
                Intervention.deleted_at.is_(None),
            )
            .first()
        )

        if not intervention:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Intervention not found for this org",
            )

        if data.event_type == EventType.CREATED:
            existing_created = (
                db.query(Event)
                .filter(
                    Event.intervention_id == intervention.id,
                    Event.event_type == EventType.CREATED,
                )
                .first()
            )
            if existing_created:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A 'CREATED' event already exists for this intervention",
                )

        elif data.event_type == EventType.STATUS_CHANGED:
            if data.new_status is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="'new_status' must be provided for status_changed events",
                )
            new_status = data.new_status.value
            if not new_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="'new_status' must be provided for status_changed events",
                )

            allowed_transitions = {
                "PENDING": ["IN_PROGRESS"],
                "IN_PROGRESS": ["COMPLETED", "CANCELLED"],
                "COMPLETED": [],
                "CANCELLED": [],
            }

            old_status = intervention.status

            if new_status not in allowed_transitions[old_status.value]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Invalid status transition from {old_status.value} to {new_status}",
                )

            if data.message is None:
                data.message = f"Status changed from {old_status.value} to {new_status}"

            intervention.status = InterventionStatus(new_status)

        event = Event(
            intervention_id=intervention.id,
            event_type=data.event_type,
            message=data.message,
        )

        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def list_events(db: Session, intervention_id: UUID, org: str):
        """
        Récupère la liste chronologique de tous les événements d'une intervention.
        Vérifie que l'intervention appartient à l'organisation spécifiée.
        """
        intervention_exists = (
            db.query(Intervention.id)
            .filter(
                Intervention.id == intervention_id,
                Intervention.org == org,
                Intervention.deleted_at.is_(None),
            )
            .first()
        )

        if not intervention_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intervention not found"
            )

        return (
            db.query(Event)
            .filter(Event.intervention_id == intervention_id)
            .order_by(Event.created_at.asc())
            .all()
        )
