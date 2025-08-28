# GarageOS API - Document de Conception

## Vue d'ensemble

GarageOS est une API REST pour la gestion d'interventions automobiles, conçue avec FastAPI et SQLAlchemy. L'architecture suit le pattern Repository avec une séparation claire entre les couches API, service et données.

## Choix d'architecture

### Multi-tenancy par Organisation

- **Isolation** : Chaque organisation a ses propres données (clients, techniciens, interventions)
- **Sécurité** : Authentification JWT avec scope organisationnel
- **Simplicité** : Pas de complexité de base de données partagée

### Authentification JWT

- **Stateless** : Pas de session serveur à maintenir
- **Scalabilité** : Facilite le déploiement multi-instances
- **Sécurité** : Tokens avec expiration et validation cryptographique

### Modélisation des données

#### Clients

- **Contraintes** : Email unique par organisation, téléphone formaté
- **Soft delete** : Conservation historique avec flag `deleted`

#### Interventions

- **Workflow** : Statuts avec transitions contrôlées (PENDING → IN_PROGRESS → COMPLETED ou CANCELLED)
- **Assignation** : Technicien obligatoire pour chaque intervention
- **Traçabilité** : Événements automatiques sur création/modification

#### Événements

- **Timeline** : Historique complet des actions sur les interventions
- **Types** : CREATED, STATUS_CHANGED, NOTE
- **Audit** : Traçabilité complète pour conformité

## Arbitrages techniques

### Base de données

- **SQLite** : Simplicité pour le développement et les tests
- **PostgreSQL** : Recommandé pour la production (UUID natif, contraintes avancées)

### Validation

- **Pydantic** : Validation automatique des schémas API
- **SQLAlchemy** : Validation au niveau base de données

### Tests

- **Base mémoire** : Tests isolés et rapides
- **Fixtures** : Données de test cohérentes et réutilisables

## Règles métier

1. **Transitions de statut** : PENDING → IN_PROGRESS → COMPLETED ou CANCELLED(pas de retour arrière)
2. **Unicité email** : Par organisation, pas globalement
3. **Technicien obligatoire** : Toute intervention doit avoir un technicien assigné
4. **Soft delete** : Pas de suppression physique des données
5. **Isolation organisationnelle** : Accès strict aux données de l'organisation
