from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.intervention import (
    InterventionCreate,
    InterventionRead,
    InterventionUpdate,
)
from app.services.intervention import InterventionService
from app.api.deps import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/interventions", tags=["interventions"])


@router.post("", response_model=InterventionRead, status_code=status.HTTP_201_CREATED)
def create_intervention(
    data: InterventionCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Créer une nouvelle intervention.

    - **client_id** : Identifiant du client (obligatoire)
    - **technician_id** : Identifiant du technicien assigné (obligatoire)
    - **status** : Statut initial de l'intervention (PENDING, IN_PROGRESS, COMPLETED)
    - **description** : Description détaillée de l'intervention

    Un événement CREATED est automatiquement créé lors de la création.
    """
    org = current["org"]
    return InterventionService.create_item(db, data, org)


@router.get("", response_model=List[InterventionRead])
def list_interventions(
    status_eq: str | None = None,
    client_id: int | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Récupérer la liste des interventions de l'organisation.

    - **status_eq** : Filtrer par statut (PENDING, IN_PROGRESS, COMPLETED)
    - **client_id** : Filtrer par client spécifique
    - **q** : Terme de recherche dans la description
    - **limit** : Nombre maximum d'interventions (défaut: 50)
    - **offset** : Nombre d'interventions à ignorer pour la pagination

    Retourne une liste paginée des interventions filtrées.
    """
    org = current["org"]
    return InterventionService.list_items(
        db, org, limit, offset, status_eq, client_id, q
    )


@router.get("/{intervention_id}", response_model=InterventionRead)
def get_intervention(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Récupérer les détails d'une intervention spécifique.

    - **intervention_id** : Identifiant unique de l'intervention

    Retourne les données complètes de l'intervention si elle existe dans l'organisation.
    """
    org = current["org"]
    return InterventionService.get_item(db, intervention_id, org)


@router.patch("/{intervention_id}", response_model=InterventionRead)
def update_intervention(
    intervention_id: UUID,
    data: InterventionUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Mettre à jour une intervention existante.

    - **intervention_id** : Identifiant unique de l'intervention
    - **data** : Données à mettre à jour (tous les champs sont optionnels)

    **Règles de transition de statut :**
    - PENDING → IN_PROGRESS → COMPLETED ou CANCELLED
    - Pas de retour en arrière possible
    - Transition directe PENDING → COMPLETED interdite

    Un événement STATUS_CHANGED est automatiquement créé lors du changement de statut.
    """
    org = current["org"]
    return InterventionService.update_item(db, intervention_id, data, org)


@router.delete("/{intervention_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_intervention(
    intervention_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Supprimer une intervention (suppression logique).

    - **intervention_id** : Identifiant unique de l'intervention

    Effectue une suppression logique de l'intervention (marquée comme supprimée mais conservée en base).
    """
    org = current["org"]
    return InterventionService.delete_item(db, intervention_id, org)
