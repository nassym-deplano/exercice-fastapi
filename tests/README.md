# Tests pour l'API FastAPI

Ce répertoire contient les tests pour l'API FastAPI de gestion d'interventions.

## Fichiers de test

- `test_smoke.py` - Tests de base (health, authentification)
- `test_business.py` - Tests de logique métier (CRUD, règles de transition, timeline)

## Exécution des tests

### Prérequis

```bash
pip install pytest
```

### Exécuter tous les tests

```bash
pytest
```

### Exécuter un fichier spécifique

```bash
pytest tests/test_smoke.py
pytest tests/test_business.py
```

### Mode verbose

```bash
pytest -v
```

### Mode debug

```bash
pytest -s
```

## Types de tests

### Tests de base (`test_smoke.py`)

- Endpoint `/health`
- Authentification JWT
- Rejet des requêtes sans token
- Documentation de l'API

### Tests métier (`test_business.py`)

- **Opérations clients** : création, liste, récupération, validation des doublons
- **Opérations interventions** : création, assignation technicien, validation client
- **Transitions de statut** : règles de transition autorisées/interdites
- **Timeline d'événements** : création automatique d'événements

## Configuration

Les tests utilisent :

- Base de données SQLite en mémoire
- Fixtures pytest pour la réutilisation
- Override des dépendances pour l'isolation
- Nettoyage automatique après chaque test

## Points importants

1. **Authentification** : Tous les tests métier nécessitent un token JWT valide
2. **Isolation** : Chaque test est isolé avec sa propre session de base de données
3. **Fixtures** : Réutilisation des données de test (utilisateur, client, technicien)
4. **Validation** : Tests des règles métier (unicité email, transitions de statut)
