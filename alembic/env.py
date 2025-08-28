import sys
import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.db.base import Base

from app.models.client import Client  # noqa: F401
from app.models.technician import Technician  # noqa: F401
from app.models.intervention import Intervention  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.user import User  # noqa: F401

config = context.config

# Source unique de vérité: settings.DATABASE_URL (.env)
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    kwargs = dict(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=_is_sqlite(url),  # nécessaire pour ALTER sous SQLite
    )
    context.configure(**kwargs)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool, future=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=_is_sqlite(url),
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
