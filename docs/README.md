# GarageOS API - Documentation

## Vue d'ensemble

GarageOS est une API REST complète pour la gestion d'interventions automobiles. Elle permet de gérer les clients, techniciens, interventions et événements dans un contexte multi-organisationnel.

### Fonctionnalités principales

- **Gestion des clients** : CRUD complet avec validation des données
- **Gestion des techniciens** : Équipe technique et assignations
- **Interventions** : Workflow complet avec statuts et transitions
- **Événements** : Timeline et audit trail automatique
- **Authentification** : JWT avec gestion des organisations
- **Multi-tenancy** : Isolation complète par organisation

## Schéma de l'API

### Endpoints principaux

```
POST   /auth/login          # Authentification
POST   /auth/signup         # Inscription

GET    /clients             # Liste des clients
POST   /clients             # Créer un client
GET    /clients/{id}        # Détails d'un client
PATCH  /clients/{id}        # Modifier un client
DELETE /clients/{id}        # Supprimer un client

GET    /technicians         # Liste des techniciens
POST   /technicians         # Créer un technicien
GET    /technicians/{id}    # Détails d'un technicien
PATCH  /technicians/{id}    # Modifier un technicien
DELETE /technicians/{id}    # Supprimer un technicien

GET    /interventions       # Liste des interventions
POST   /interventions       # Créer une intervention
GET    /interventions/{id}  # Détails d'une intervention
PATCH  /interventions/{id}  # Modifier une intervention
DELETE /interventions/{id}  # Supprimer une intervention

GET    /interventions/{id}/events  # Événements d'une intervention
POST   /interventions/{id}/events  # Créer un événement

GET    /health              # Santé de l'API
```

## Authentification

### JWT Token

Toutes les routes métier nécessitent un token JWT valide dans le header `Authorization` :

```http
Authorization: Bearer <token>
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Réponse :**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Modèles de données

### Client

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "org": "org_alpha",
  "name": "Jean Dupont",
  "email": "jean.dupont@email.com",
  "phone": "+33123456789",
  "deleted": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "deleted_at": null
}
```

### Technicien

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440000",
  "org": "org_alpha",
  "name": "Pierre Martin",
  "email": "pierre.martin@garage.com",
  "deleted": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "deleted_at": null
}
```

### Intervention

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "org": "org_alpha",
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "technician_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "IN_PROGRESS",
  "description": "Réparation du système de freinage - remplacement des plaquettes",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z",
  "deleted_at": null
}
```

### Événement

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "intervention_id": "770e8400-e29b-41d4-a716-446655440000",
  "event_type": "STATUS_CHANGED",
  "message": "Statut changé de PENDING vers IN_PROGRESS",
  "created_at": "2024-01-15T11:45:00Z"
}
```

## Règles métier

### 1. Transitions de statut des interventions

Les interventions suivent un workflow strict :

```
PENDING → IN_PROGRESS → COMPLETED ou CANCELLED
```

- **PENDING** : Intervention créée, en attente de prise en charge
- **IN_PROGRESS** : Intervention en cours de réalisation
- **COMPLETED** : Intervention terminée
- **CANCELLED** : Intervention annulée

**Règles :**

- Pas de retour en arrière possible
- Transition directe PENDING → COMPLETED interdite
- Seul le statut peut être modifié via PATCH

### 2. Unicité des emails

- **Clients** : Email unique par organisation
- **Techniciens** : Email unique par organisation
- **Utilisateurs** : Email unique globalement

### 3. Assignation des techniciens

- Toute intervention doit avoir un technicien assigné
- Le technicien peut être modifié à tout moment
- Un technicien peut être assigné à plusieurs interventions

### 4. Soft delete

- Toutes les suppressions sont logiques (flag `deleted`)
- Les données supprimées restent en base pour audit
- Les listes n'incluent que les éléments non supprimés

### 5. Isolation organisationnelle

- Chaque utilisateur appartient à une organisation
- Accès strict aux données de l'organisation
- Pas de fuite de données entre organisations

## Exemples d'utilisation

### Créer un client

```http
POST /clients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Marie Dubois",
  "email": "marie.dubois@email.com",
  "phone": "+33123456789"
}
```

**Réponse (201) :**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "org": "org_alpha",
  "name": "Marie Dubois",
  "email": "marie.dubois@email.com",
  "phone": "+33123456789",
  "deleted": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "deleted_at": null
}
```

### Créer une intervention

```http
POST /interventions
Authorization: Bearer <token>
Content-Type: application/json

{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "technician_id": "660e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "description": "Vidange et remplacement du filtre à huile"
}
```

### Modifier le statut d'une intervention

```http
PATCH /interventions/770e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "IN_PROGRESS"
}
```

### Lister les interventions avec pagination

```http
GET /interventions?limit=10&offset=0&status_eq=IN_PROGRESS
Authorization: Bearer <token>
```

## Gestion des erreurs

### Codes de statut HTTP

- **200** : Succès (GET, PATCH)
- **201** : Créé avec succès (POST)
- **204** : Supprimé avec succès (DELETE)
- **400** : Requête invalide
- **401** : Non authentifié
- **403** : Non autorisé
- **404** : Ressource non trouvée
- **409** : Conflit (email dupliqué, transition invalide)
- **422** : Erreur de validation

### Format des erreurs

```json
{
  "detail": "Message d'erreur descriptif"
}
```

### Exemples d'erreurs

#### 401 - Non authentifié

```json
{
  "detail": "Could not validate credentials"
}
```

#### 409 - Email dupliqué

```json
{
  "detail": "Email already exists in this organization"
}
```

#### 409 - Transition de statut invalide

```json
{
  "detail": "Invalid status transition from PENDING to COMPLETED"
}
```

#### 422 - Validation échouée

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required"
    }
  ]
}
```

## Pagination

Les endpoints de liste supportent la pagination :

- **limit** : Nombre d'éléments par page (défaut: 50, max: 100)
- **offset** : Nombre d'éléments à ignorer

```http
GET /clients?limit=20&offset=40
```

## Recherche

Certains endpoints supportent la recherche textuelle :

```http
GET /clients?q=dupont
GET /interventions?q=freinage
```

## Tests

### Lancer les tests

```bash
# Tous les tests
make test

# Tests de fumée (authentification, santé)
make test-smoke

# Tests métier
make test-business
```

### Structure des tests

- **test_smoke.py** : Tests d'infrastructure et d'authentification
- **test_business.py** : Tests des règles métier et workflows

## Développement

### Installation

```bash
pip install -r requirements.txt
```

### Base de données

```bash
# Initialiser la base
make init-db

# Créer une migration
make revise

# Appliquer les migrations
make init-db
```

### Démarrage

```bash
make dev
```

L'API sera disponible sur `http://localhost:8000`

### Documentation interactive

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`
