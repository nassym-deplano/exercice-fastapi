from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.event import EventCreate, EventRead
from app.services.event import EventService
from app.api.deps import get_current_user
from app.db.session import get_db


router = APIRouter(prefix="/interventions/{intervention_id}/events", tags=["events"])

@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate, 
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    return EventService.create_event(db, data, org)

@router.get("", response_model=List[EventRead])
def list_events(
    intervention_id: UUID, 
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    org = current["org"]
    return EventService.list_events(db, intervention_id, org)
