import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
from app.models.client import Client
from app.models.technician import Technician
from app.models.intervention import Intervention, InterventionStatus
from app.models.event import Event, EventType
from app.core.security import create_access_token, hash_password
from uuid import uuid4

client = TestClient(app)


@pytest.fixture(scope="session")
def test_database():
    """Crée une base de données de test temporaire."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Nettoyage
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_database):
    """Crée une session de base de données pour chaque test."""
    connection = test_database.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection
    )
    session = TestingSessionLocal()

    # Override la dépendance get_db
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # Nettoyage
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Crée un utilisateur de test."""
    user_id = uuid4()
    user = User(
        id=user_id,
        email="test@example.com",
        password=hash_password("testpassword"),
        org="org_alpha",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Crée des headers d'authentification valides."""
    token = create_access_token(
        data={"sub": str(test_user.id), "org": "org_alpha"}, expires_delta=None
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_client(db_session):
    """Crée un client de test."""
    client_obj = Client(
        id=uuid4(),
        name="Client Test",
        email="client@test.com",
        phone="0123456789",
        org="org_alpha",
        deleted=False,
    )
    db_session.add(client_obj)
    db_session.commit()
    db_session.refresh(client_obj)
    return client_obj


@pytest.fixture
def test_technician(db_session):
    """Crée un technicien de test."""
    tech = Technician(
        id=uuid4(),
        name="Technicien Test",
        email="tech@test.com",
        org="org_alpha",
        deleted=False,
    )
    db_session.add(tech)
    db_session.commit()
    db_session.refresh(tech)
    return tech


class TestClientOperations:
    """Tests pour les opérations sur les clients."""

    def test_create_client_success(self, auth_headers):
        """Test de création réussie d'un client."""
        client_data = {
            "name": "Nouveau Client",
            "email": "nouveau@client.com",
            "phone": "0123456789",
        }

        response = client.post("/clients", json=client_data, headers=auth_headers)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == client_data["name"]
        assert data["email"] == client_data["email"]
        assert data["phone"] == client_data["phone"]
        assert "id" in data
        assert data["org"] == "org_alpha"

    def test_create_client_duplicate_email(self, auth_headers, test_client):
        """Test que la création d'un client avec un email existant échoue."""
        client_data = {
            "name": "Autre Client",
            "email": test_client.email,
            "phone": "0987654321",
        }

        response = client.post("/clients", json=client_data, headers=auth_headers)
        assert response.status_code == 409
        assert "email already exists" in response.json()["detail"]

    def test_list_clients(self, auth_headers, test_client):
        """Test de récupération de la liste des clients."""
        response = client.get("/clients", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Vérifier que notre client de test est dans la liste
        client_ids = [c["id"] for c in data]
        assert str(test_client.id) in client_ids

    def test_get_client(self, auth_headers, test_client):
        """Test de récupération d'un client spécifique."""
        response = client.get(f"/clients/{test_client.id}", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == str(test_client.id)
        assert data["name"] == test_client.name
        assert data["email"] == test_client.email

    def test_get_client_not_found(self, auth_headers):
        """Test de récupération d'un client inexistant."""
        fake_id = uuid4()
        response = client.get(f"/clients/{fake_id}", headers=auth_headers)
        assert response.status_code == 404


class TestInterventionOperations:
    """Tests pour les opérations sur les interventions."""

    def test_create_intervention_success(
        self, auth_headers, test_client, test_technician
    ):
        """Test de création réussie d'une intervention."""
        client_id = str(test_client.id)
        technician_id = str(test_technician.id)

        intervention_data = {
            "client_id": client_id,
            "technician_id": technician_id,
            "status": "PENDING",
            "description": "Nouvelle intervention",
        }

        response = client.post(
            "/interventions", json=intervention_data, headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["description"] == intervention_data["description"]
        assert data["client_id"] == client_id
        assert data["technician_id"] == technician_id
        assert data["status"] == "PENDING"
        assert "id" in data

    def test_create_intervention_client_not_found(self, auth_headers, test_technician):
        """Test de création d'une intervention avec un client inexistant."""
        fake_client_id = uuid4()
        intervention_data = {
            "client_id": str(fake_client_id),
            "description": "Intervention test",
            "technician_id": str(test_technician.id),
            "status": "PENDING",
        }

        response = client.post(
            "/interventions", json=intervention_data, headers=auth_headers
        )
        assert response.status_code == 404
        assert "Client not found" in response.json()["detail"]


class TestStatusTransitions:
    """Tests pour les règles de transition de statut."""

    def test_valid_status_transitions(self, auth_headers, test_client, test_technician):
        """Test des transitions de statut valides."""
        # Créer une intervention
        intervention_data = {
            "client_id": str(test_client.id),
            "description": "Intervention pour test de statut",
            "technician_id": str(test_technician.id),
            "status": "PENDING",
        }

        response = client.post(
            "/interventions", json=intervention_data, headers=auth_headers
        )
        assert response.status_code == 201
        intervention_id = response.json()["id"]

        # PENDING -> IN_PROGRESS
        update_data = {"status": "IN_PROGRESS"}
        response = client.patch(
            f"/interventions/{intervention_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "IN_PROGRESS"

        # IN_PROGRESS -> COMPLETED
        update_data = {"status": "COMPLETED"}
        response = client.patch(
            f"/interventions/{intervention_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "COMPLETED"

    def test_invalid_status_transitions(
        self, auth_headers, test_client, test_technician
    ):
        """Test des transitions de statut invalides."""
        # Créer une intervention
        intervention_data = {
            "client_id": str(test_client.id),
            "description": "Intervention pour test invalide",
            "technician_id": str(test_technician.id),
            "status": "PENDING",
        }

        response = client.post(
            "/interventions", json=intervention_data, headers=auth_headers
        )
        assert response.status_code == 201
        intervention_id = response.json()["id"]

        # PENDING -> COMPLETED (invalide)
        update_data = {"status": "COMPLETED"}
        response = client.patch(
            f"/interventions/{intervention_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 409
        assert "Invalid status transition" in response.json()["detail"]


class TestEventTimeline:
    """Tests pour la timeline des événements."""

    def test_event_creation_on_intervention_create(
        self, auth_headers, test_client, test_technician
    ):
        """Test qu'un événement CREATED est créé lors de la création d'une intervention."""
        intervention_data = {
            "client_id": str(test_client.id),
            "description": "Intervention pour timeline",
            "technician_id": str(test_technician.id),
            "status": "PENDING",
        }

        response = client.post(
            "/interventions", json=intervention_data, headers=auth_headers
        )
        assert response.status_code == 201

        intervention_id = response.json()["id"]

        # Vérifier les événements
        events_response = client.get(
            f"/interventions/{intervention_id}/events", headers=auth_headers
        )
        assert events_response.status_code == 200

        events = events_response.json()
        assert len(events) == 1
        assert events[0]["event_type"] == "CREATED"
        assert "Intervention created for client" in events[0]["message"]

    def test_event_creation_on_status_change(
        self, auth_headers, test_client, test_technician
    ):
        """Test qu'un événement STATUS_CHANGED est créé lors du changement de statut."""
        # Créer une intervention
        intervention_data = {
            "client_id": str(test_client.id),
            "description": "Intervention pour test d'événements",
            "technician_id": str(test_technician.id),
            "status": "PENDING",
        }

        response = client.post(
            "/interventions", json=intervention_data, headers=auth_headers
        )
        assert response.status_code == 201
        intervention_id = response.json()["id"]

        # Changer le statut
        update_data = {"status": "IN_PROGRESS"}
        response = client.patch(
            f"/interventions/{intervention_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200

        # Vérifier les événements
        events_response = client.get(
            f"/interventions/{intervention_id}/events", headers=auth_headers
        )
        assert events_response.status_code == 200

        events = events_response.json()
        assert len(events) >= 1

        # Trouver l'événement de changement de statut
        status_events = [e for e in events if e["event_type"] == "STATUS_CHANGED"]
        assert len(status_events) >= 1

        status_event = status_events[0]
        assert "PENDING" in status_event["message"]
        assert "IN_PROGRESS" in status_event["message"]
