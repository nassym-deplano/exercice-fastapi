# Étude de cas FastAPI (GarageOS)

## Lancer rapidement

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make init-db-lite   # crée le fichier SQLite si vous gardez DATABASE_URL=sqlite://...
make dev
```

## Docker

### Prérequis

- Docker + Docker Compose

### Démarrer avec Docker Compose (app + Postgres)

1. Copier l'exemple d'env et ajuster si besoin:

```
cp env.docker.example .env
```

2. Lancer les services:

```
docker compose up --build
```

3. L'application est disponible sur `http://localhost:8000`:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

La base Postgres est exposée sur `localhost:5432`.
