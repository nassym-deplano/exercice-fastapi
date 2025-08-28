from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.schemas.technician import TechnicianCreate, TechnicianRead, TechnicianUpdate
from app.services.technician import TechnicianService
from app.api.deps import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/technicians", tags=["technicians"])


@router.post("", response_model=TechnicianRead, status_code=status.HTTP_201_CREATED)
def create_technician(
    data: TechnicianCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    return TechnicianService.create_technician(db, data, org)


@router.get("", response_model=List[TechnicianRead])
def list_technicians(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    return TechnicianService.list_technicians(db, org, limit, offset, q)


@router.get("/{tech_id}", response_model=TechnicianRead)
def get_technician(
    tech_id: UUID, 
    db: Session = Depends(get_db), 
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    return TechnicianService.get_technician(db, tech_id, org)


@router.patch("/{tech_id}", response_model=TechnicianRead)
def update_technician(
    tech_id: UUID, 
    data: TechnicianUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    return TechnicianService.update_technician(db, tech_id, data, org)


@router.delete("/{tech_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_technician(
    tech_id: UUID, 
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    TechnicianService.delete_technician(db, tech_id, org)
