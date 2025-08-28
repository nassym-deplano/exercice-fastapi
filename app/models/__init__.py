# Importez vos modèles ici pour que Alembic les détecte lors de l'autogénération :
from app.models.technician import Technician  # noqa: F401
from app.models.client import Client  # noqa: F401
from app.models.intervention import Intervention, InterventionStatus  # noqa: F401
from app.models.event import Event, EventType  # noqa: F401
from app.models.user import User