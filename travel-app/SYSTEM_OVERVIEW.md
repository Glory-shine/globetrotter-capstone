# Travel App System Overview

Ce document décrit le dossier `travel-app`, le fonctionnement du backend, et l'API exposée.

## 1. Architecture générale

`travel-app` est une application monolithique : tout le backend s'exécute dans une seule application FastAPI, avec une persistance de données stockée dans un fichier JSON plat.

Structure principale du dossier :

- `app/`
  - `main.py` : point d'entrée de FastAPI, configuration CORS, enregistrement des routeurs
  - `auth.py` : gestion de l'authentification JWT, hachage des mots de passe
  - `storage.py` : couche d'accès aux données via un fichier JSON, lecture/écriture atomiques
  - `models.py` : schémas Pydantic pour les requêtes et réponses
  - `recommendation.py` : logique de recommandation des destinations
  - `trip_planner.py` : logique métier pour les itinéraires
  - `routers/`
    - `auth_routes.py` : routes `/register` et `/login`
    - `destinations.py` : route `/destinations`
    - `recommendations.py` : route `/recommendations`
    - `itineraries.py` : routes `/itineraries`
  - `data/db.json` : base de données JSON plat stockant utilisateurs, destinations, et itinéraires
- `tests/` : tests pytest couvrant API et composants métier
- `requirements.txt` : dépendances Python
- `pytest.ini` : configuration de tests

## 2. Flux de données et fonctionnement

### a. Lecture et écriture des données

- `app/storage.py` est la seule source de lecture et d'écriture de `app/data/db.json`.
- Les fonctions `read_data()` et `write_data()` sont asynchrones et déchargent le travail I/O sur un thread dédié via `asyncio.to_thread()`.
- Les écritures sont atomiques : les données sont d'abord écrites dans un fichier temporaire puis remplacent le fichier final avec `os.replace()`.
- Un verrou `threading.RLock()` garantit qu'une seule opération de lecture/écriture se produit à la fois.

### b. Authentification

- Les routes d'inscription et de connexion sont définies dans `app/routers/auth_routes.py`.
- `app/auth.py` fournit :
  - `hash_password(password)` : génère un hash PBKDF2-HMAC-SHA256 avec sel
  - `verify_password(password, stored_hash)` : vérifie un mot de passe
  - `create_access_token(data)` : génère un JWT signé
  - `decode_access_token(token)` : vérifie et décode un JWT
  - `get_current_user()` : dépendance FastAPI qui extrait l'utilisateur connecté depuis le JWT
- L'application est stateless côté serveur : le client conserve le JWT.

### c. Gestion des destinations

- `app/routers/destinations.py` lit toutes les destinations depuis le JSON.
- La route `GET /destinations` prend en charge les filtres :
  - `country` : filtrage exact insensible à la casse
  - `tag` : filtrage par tag de destination
  - `max_cost` : coût moyen journalier maximum
  - `q` : recherche texte dans `name` et `description`
- La réponse est un tableau d'objets `DestinationOut` défini dans `app/models.py`.

### d. Recommandations

- `app/routers/recommendations.py` expose `GET /recommendations`.
- `RecommendationEngine` dans `app/recommendation.py` calcule un score pour chaque destination :
  - correspondance de préférences utilisateur
  - historique des itinéraires déjà planifiés
  - note de la destination
  - pénalité si le budget est dépassé
- Le résultat est une liste triée de destinations personnalisées.

### e. Itinéraires

- `app/routers/itineraries.py` gère la création et la récupération des itinéraires.
- Les itinéraires sont stockés dans la base JSON avec :
  - `id`
  - `user_id`
  - `destination_id`
  - `title`
  - `start_date`/`end_date`
  - `items` (activités par jour)
  - `created_at`
- Les itinéraires sont liés à l'utilisateur connecté via le JWT.

## 3. API exposée

### Route publique

- `POST /register`
  - Enregistre un nouvel utilisateur
  - Reçoit : `username`, `email`, `password`, `preferences`
  - Retourne : `access_token`, `token_type`

- `POST /login`
  - Authentifie un utilisateur existant
  - Reçoit : `username`, `password`
  - Retourne : `access_token`, `token_type`

- `GET /health`
  - Vérifie simplement l'état de l'application
  - Retourne : `{"status": "ok"}`

### Routes protégées (requièrent `Authorization: Bearer <token>`)

- `GET /destinations`
  - Recherche et filtre les destinations
  - Paramètres : `country`, `tag`, `max_cost`, `q`
  - Retourne : liste d'objets destination

- `GET /recommendations`
  - Retourne des destinations recommandées
  - Paramètres : `limit` (max 20), `max_budget`
  - Retourne : liste d'objets destination

- `POST /itineraries`
  - Crée un nouvel itinéraire
  - Corps JSON : `title`, `destination_id`, `start_date`, `end_date`, `items`
  - Validation : `end_date` doit être le même jour ou après `start_date`

- `GET /itineraries`
  - Renvoie les itinéraires de l'utilisateur connecté

## 4. Comportement de test

- `tests/` contient les tests pytest qui utilisent `TestClient` de FastAPI.
- Chaque test configure `TRAVEL_APP_DB_PATH` vers un fichier temporaire isolé.
- Cela garantit l'indépendance des tests et évite les collisions entre exécutions.

## 5. Points importants

- Ce backend est conçu pour rester simple et monolithique.
- Il n'utilise pas de base de données relationnelle : tout est stocké dans `app/data/db.json`.
- L'authentification est stateless, ce qui facilite l'intégration avec un frontend séparé.
- Le système peut être étendu en ajoutant de nouvelles routes dans `app/routers`, en enrichissant les modèles Pydantic, ou en améliorant la logique métier dans `recommendation.py` et `trip_planner.py`.
