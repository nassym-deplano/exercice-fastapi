import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User
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
        org="org_alpha"
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


def test_health_ok():
    """Test que l'endpoint /health fonctionne correctement."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_requires_jwt_on_business_routes():
    """Test que les routes métier nécessitent une authentification."""
    assert client.get("/clients").status_code == 401
    assert client.get("/technicians").status_code == 401
    assert client.get("/interventions").status_code == 401
    assert client.get("/interventions/123e4567-e89b-12d3-a456-426614174000/events").status_code == 401


def test_business_routes_with_valid_jwt(auth_headers):
    """Test que les routes métier fonctionnent avec un token JWT valide."""
    # Les endpoints peuvent retourner 200 (succès), 404 (non trouvé), ou 501 (non implémenté)
    response = client.get("/clients", headers=auth_headers)
    assert response.status_code in [200, 404, 501]

    response = client.get("/technicians", headers=auth_headers)
    assert response.status_code in [200, 404, 501]

    response = client.get("/interventions", headers=auth_headers)
    assert response.status_code in [200, 404, 501]

    response = client.get("/interventions/123e4567-e89b-12d3-a456-426614174000/events", headers=auth_headers)
    assert response.status_code in [200, 404, 501]


def test_invalid_jwt_token():
    """Test que les tokens JWT invalides sont rejetés."""
    invalid_headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/clients", headers=invalid_headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]


def test_missing_jwt_token():
    """Test que les requêtes sans token sont rejetées."""
    response = client.get("/clients")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_api_documentation_available():
    """Test que la documentation de l'API est accessible."""
    # Test de l'endpoint OpenAPI
    response = client.get("/openapi.json")
    assert response.status_code == 200

    # Test de l'interface Swagger
    response = client.get("/docs")
    assert response.status_code == 200

    # Test de l'interface ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200
