from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import SecurityHeadersMiddleware
from app.api.routers import health, clients, technicians, interventions, events, auth

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    GarageOS API - Système de gestion d'interventions automobiles
    
    Cette API permet de gérer les interventions automobiles avec un système complet de clients, techniciens, interventions et événements.
    
    -Fonctionnalités principales
    
    * Gestion des clients : Création, consultation et modification des clients
    * Gestion des techniciens : Gestion de l'équipe technique
    * Interventions : Création et suivi des interventions automobiles
    * Événements : Timeline des événements pour chaque intervention
    * Authentification : Système JWT avec gestion des organisations
    
    -Authentification
    
    Toutes les routes métier nécessitent une authentification JWT. Incluez le token dans le header `Authorization: Bearer <token>`.
    
    -Organisations
    
    L'API supporte la multi-tenancy avec des organisations isolées. Chaque utilisateur appartient à une organisation.
    """,
    version="1.0.0",
    contact={
        "name": "GarageOS Support",
        "email": "support@garageos.com",
    },
)

# Security headers & CORS
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)

# Routers
app.include_router(health.router)
app.include_router(clients.router)
app.include_router(technicians.router)
app.include_router(interventions.router)
app.include_router(events.router)
app.include_router(auth.router)
