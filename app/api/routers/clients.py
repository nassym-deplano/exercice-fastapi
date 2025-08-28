from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.schemas.client import ClientRead, ClientCreate, ClientUpdate
from app.services.client import ClientService
from app.api.deps import get_current_user
from app.db.session import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Créer un nouveau client.

    - **name**: Nom complet du client
    - **email**: Adresse email (doit être unique dans l'organisation)
    - **phone**: Numéro de téléphone (format international accepté)

    Retourne les données du client créé avec son identifiant unique.
    """
    org = current["org"]
    return ClientService.create_client(db, data, org)


@router.get("", response_model=List[ClientRead])
def list_clients(
    limit: int = 50,
    offset: int = 0,
    q: str | None = None,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Récupérer la liste des clients de l'organisation.

    - **limit**: Nombre maximum de clients à retourner (défaut: 50)
    - **offset**: Nombre de clients à ignorer pour la pagination (défaut: 0)
    - **q**: Terme de recherche optionnel (recherche dans nom et email)

    Retourne une liste paginée des clients de l'organisation.
    """
    org = current["org"]
    return ClientService.list_clients(db, org, limit, offset, q)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Récupérer les détails d'un client spécifique.

    - **client_id**: Identifiant unique du client

    Retourne les données complètes du client s'il existe dans l'organisation.
    """
    org = current["org"]
    return ClientService.get_client(db, client_id, org)


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: UUID,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Mettre à jour les informations d'un client.

    - **client_id**: Identifiant unique du client
    - **data**: Données à mettre à jour (tous les champs sont optionnels)

    Retourne les données mises à jour du client.
    """
    org = current["org"]
    return ClientService.update_client(db, client_id, data, org)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user),
):
    """
    Supprimer un client (suppression logique).

    - **client_id**: Identifiant unique du client

    Effectue une suppression logique du client (marqué comme supprimé mais conservé en base).
    """
    org = current["org"]
    ClientService.delete_client(db, client_id, org)
