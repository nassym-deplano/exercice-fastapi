from datetime import datetime, UTC
from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.schemas.technician import TechnicianCreate, TechnicianUpdate, TechnicianRead
from app.models.technician import Technician


class TechnicianService:

    @staticmethod
    def create_technician(
        db: Session, data: TechnicianCreate, org: str
    ) -> TechnicianRead:
        """
        Crée un nouveau technicien dans l'organisation spécifiée.
        Vérifie l'unicité de l'email avant la création.
        """
        existing = db.scalar(
            select(Technician).where(
                Technician.org == org,
                Technician.email == data.email,
                Technician.deleted == False,
            )
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Technician with this email already exists",
            )

        tech = Technician(**data.model_dump(), org=org)
        db.add(tech)
        db.commit()
        db.refresh(tech)
        return tech

    @staticmethod
    def list_technicians(
        db: Session, org: str, limit: int = 50, offset: int = 0, q: str | None = None
    ) -> List[TechnicianRead]:
        """
        Récupère la liste des techniciens d'une organisation avec pagination et recherche.
        Permet de filtrer par nom ou email si un terme de recherche est fourni.
        """
        query = select(Technician).where(
            Technician.org == org, Technician.deleted == False
        )
        if q:
            query = query.where(
                or_(Technician.name.ilike(f"%{q}%"), Technician.email.ilike(f"%{q}%"))
            )
        return db.scalars(query.limit(limit).offset(offset)).all()

    @staticmethod
    def get_technician(db: Session, tech_id: UUID, org: str) -> TechnicianRead:
        """
        Récupère un technicien spécifique par son ID dans l'organisation donnée.
        """
        tech = db.scalar(
            select(Technician).where(
                Technician.id == tech_id,
                Technician.org == org,
                Technician.deleted == False,
            )
        )
        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Technician not found"
            )
        return tech

    @staticmethod
    def update_technician(
        db: Session, tech_id: UUID, data: TechnicianUpdate, org: str
    ) -> TechnicianRead:
        """
        Met à jour les informations d'un technicien existant.
        Seuls les champs fournis dans les données sont modifiés.
        """
        tech = TechnicianService.get_technician(db, tech_id, org)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tech, field, value)
        db.commit()
        db.refresh(tech)
        return tech

    @staticmethod
    def delete_technician(db: Session, tech_id: UUID, org: str):
        """
        Supprime logiquement un technicien de la base de données.
        Le technicien n'est pas physiquement supprimé de la base de données.
        """
        tech = TechnicianService.get_technician(db, tech_id, org)
        tech.deleted = True
        tech.deleted_at = datetime.now(UTC)
        db.commit()
