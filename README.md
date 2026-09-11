# GlobeTrotter Bafoussam

Guide de voyage local pour la ville de **Bafoussam** (Ouest-Cameroun) : recherche de
lieux réels avec photos et coordonnées GPS, recommandations personnalisées,
estimation de tarifs moto-taxi/taxi entre deux lieux, activités avec leurs prix,
et planification d'itinéraires.

Architecture microservices FastAPI + PostgreSQL côté backend, Vue 3 + Vite +
Tailwind côté frontend, le tout conteneurisé avec Docker.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Démarrage rapide avec Docker (recommandé)](#démarrage-rapide-avec-docker-recommandé)
- [Démarrage manuel (sans Docker)](#démarrage-manuel-sans-docker)
- [Les données de Bafoussam](#les-données-de-bafoussam)
- [Le calcul des tarifs moto / taxi](#le-calcul-des-tarifs-moto--taxi)
- [Tests](#tests)
- [Dépannage](#dépannage)

## Fonctionnalités

- **Recherche et carte réelle** plus de 20 lieux de Bafoussam (coordonnées GPS, photos)
- **Assistant "Pour vous"** — un widget conversationnel qui propose des lieux
  selon le budget et les centres d'intérêt choisis (`GET /destinations`
  filtré côté serveur)
- **🎲 Surprends-moi** — bouton qui tire un lieu au hasard dans le catalogue
- **Tarification moto / taxi** entre deux lieux, calculée sur leur distance
  réelle (`GET /fare`)
- **Activités avec leur prix**, et une note rappelant que tous les prix
  affichés sont des **maximums indicatifs, négociables sur place**
- **Avis et commentaires** sur chaque lieu, avec réponses (un niveau) et
  système de like (`/destinations/{id}/comments`, `/comments/{id}/like`)
- **Lecture audio** de la description de chaque lieu (synthèse vocale du
  navigateur, aucun service tiers requis)
- **Anecdote « Le saviez-vous ? »** pour chaque lieu, sur sa page détail

## Architecture

```
                         ┌─────────────┐
   Frontend (Vue 3) ───▶ │ API Gateway │  :8000
                         └──────┬──────┘
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
      ┌───────────────┐ ┌────────────────┐ ┌────────────────────────┐
      │ User Service   │ │ Itinerary      │ │ Recommendation Service  │
      │ :8001          │ │ Service :8002  │ │ :8003                    │
      └───────┬────────┘ └───────┬────────┘ └──────────┬───────────────┘
              │                  │                      │
              ▼                  ▼                      ▼
         ┌─────────┐       ┌─────────────┐      ┌──────────────────┐
         │ user_db │       │ itinerary_db│      │ recommendation_db │
         └─────────┘       └─────────────┘      └──────────────────┘
              (une seule instance PostgreSQL, trois bases séparées)

   Appels synchrones (REST) :
     itinerary-service      ──▶ recommendation-service   (vérifie qu'un lieu existe)
     recommendation-service ──▶ user-service              (lit les préférences)
     recommendation-service ──▶ itinerary-service         (lit l'historique de visites)

   Événements asynchrones (RabbitMQ) :
     itinerary-service ┄▶ [exchange globetrotter.events] ┄▶ recommendation-service
                            routing key : itinerary.created
```

| Composant | Rôle | Port |
|---|---|---|
| **frontend** | Application Vue 3 (SPA) | 5173 (Docker) / 5173 (npm run dev) |
| **gateway** | Point d'entrée unique, route vers les 3 services | 8000 |
| **user-service** | Inscription, connexion, profils, préférences | 8001 |
| **itinerary-service** | Création et consultation d'itinéraires | 8002 |
| **recommendation-service** | Catalogue des lieux, recommandations, tarifs moto/taxi | 8003 |
| **postgres** | 3 bases : `user_db`, `itinerary_db`, `recommendation_db` | 5432 |
| **rabbitmq** | Messagerie événementielle + interface d'admin | 5672 / 15672 |

Le frontend ne parle **qu'au gateway**, jamais directement à un service — donc
si vous changez l'infrastructure derrière le gateway, rien ne change côté
frontend.

## Démarrage rapide avec Docker (recommandé)

Un seul terminal, une seule commande, tout démarre : Postgres, RabbitMQ, les
3 microservices, le gateway, et le frontend compilé et servi par Nginx.

**Prérequis :** Docker et Docker Compose installés.

```bash
cp .env.example .env
docker compose up --build
```

Patientez que tous les services soient "healthy" (30-60 secondes la première
fois, le temps que Postgres s'initialise et que les images se construisent),
puis ouvrez :

- **Application** : http://localhost:5173
- **Documentation interactive de l'API** (via le gateway) : http://localhost:8000/docs n'existe pas directement sur le gateway (c'est un simple proxy) — utilisez plutôt celle de chaque service : http://localhost:8001/docs, http://localhost:8002/docs, http://localhost:8003/docs
- **Santé globale du système** : http://localhost:8000/health
- **Interface d'administration RabbitMQ** : http://localhost:15672 (identifiants `guest` / `guest`)

Pour tout arrêter :

```bash
docker compose down          # arrête les conteneurs
docker compose down -v       # arrête + supprime aussi les données Postgres
```

### Vos identifiants PostgreSQL

Le fichier `.env.example` est déjà configuré avec :

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=gloire
```

Ce sont les identifiants que vous nous avez indiqués. Si votre PostgreSQL local
(hors Docker) utilise d'autres identifiants, adaptez `.env` en conséquence —
c'est la seule valeur à changer, elle est propagée automatiquement à tous les
services via `docker-compose.yml`.

## Démarrage manuel (sans Docker)

Utile si vous préférez travailler service par service, ou si Docker n'est pas
disponible sur votre machine.

### 1. PostgreSQL

Créez les 3 bases avec vos identifiants (`postgres` / `gloire`) :

```bash
psql -U postgres -c "CREATE DATABASE user_db;"
psql -U postgres -c "CREATE DATABASE itinerary_db;"
psql -U postgres -c "CREATE DATABASE recommendation_db;"
```

> Astuce : chaque service fonctionne aussi très bien avec SQLite pour du
> développement rapide sans PostgreSQL — voir plus bas.

### 2. RabbitMQ (optionnel en local)

```bash
docker run -d --name globetrotter-rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management-alpine
```

Ce n'est pas bloquant si vous ne le lancez pas : la publication/consommation
d'événements est conçue pour se dégrader silencieusement (avertissement dans
les logs) si le broker est indisponible.

### 3. Les trois microservices + le gateway

Dans 4 terminaux séparés (ou avec `&` en arrière-plan) :

```bash
# Terminal 1 — user-service
cd services/user-service
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DATABASE_URL="postgresql+psycopg://postgres:gloire@localhost:5432/user_db" \
  .venv/bin/uvicorn app.main:app --port 8001 --reload

# Terminal 2 — itinerary-service
cd services/itinerary-service
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DATABASE_URL="postgresql+psycopg://postgres:gloire@localhost:5432/itinerary_db" \
  .venv/bin/uvicorn app.main:app --port 8002 --reload

# Terminal 3 — recommendation-service
cd services/recommendation-service
python -m venv .venv && .venv/bin/pip install -r requirements.txt
DATABASE_URL="postgresql+psycopg://postgres:gloire@localhost:5432/recommendation_db" \
  .venv/bin/uvicorn app.main:app --port 8003 --reload

# Terminal 4 — gateway
cd gateway
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000 --reload
```

Pour développer sans PostgreSQL du tout, remplacez la variable
`DATABASE_URL` par `sqlite:///./dev.db` dans n'importe lequel de ces
services — c'est exactement ce que fait la suite de tests.

**Important : le même `JWT_SECRET_KEY`** doit être utilisé par les 3
services (par défaut `dev-secret-change-in-production` si vous n'en
définissez pas). Sans Docker, exportez-le explicitement pour être sûr qu'il
soit identique partout :

```bash
export JWT_SECRET_KEY="une-longue-chaine-secrete"
```

### 4. Le frontend

```bash
cd frontend
npm install
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000 par défaut, déjà correct
npm run dev
```

Ouvrez http://localhost:5173 — le frontend est configuré pour parler au
gateway sur `http://localhost:8000` par défaut, donc aucune configuration
supplémentaire n'est nécessaire si vous avez suivi les étapes précédentes.

## Les données de Bafoussam

Le catalogue de lieux (`services/recommendation-service/app/seed_data.py`)
contient 12 lieux réels de Bafoussam : la Chefferie Supérieure, son musée du
palais, le Musée des Calebasses, la Forêt Sacrée, les Marchés A et B, les
Chutes de la Metché, le Monument Wanko, la Gare Routière, le Stade Lécfo'o,
la Paroisse du Sacré-Cœur de Ndiendam, et le Festival Ngou-Ngoung.

- **Coordonnées GPS** : positionnées avec soin dans le bon quartier/commune de
  Bafoussam (I, II/Baleng, III/Bamougoum), à partir de la position confirmée
  du centre-ville (5.478°N, 10.418°E). Ce sont des estimations raisonnables
  pour une démo — pas des relevés GPS de terrain.
- **Photos réelles** : hotlinkées directement depuis Wikimedia Commons
  (`Category:Bafoussam` et `Category:Chefferie_de_Bafoussam`), pas
  téléchargées ni redistribuées — le navigateur les charge directement
  depuis Commons.
- **Prix d'entrée et activités** : estimations réalistes calibrées sur le
  seul tarif public documenté (le taxi partagé, voir plus bas), car la
  plupart des petits sites de Bafoussam n'ont pas de grille tarifaire
  officielle publiée.

Pour ajouter, modifier ou retirer un lieu, éditez simplement
`MOCK_DESTINATIONS` dans ce fichier — chaque entrée est un dictionnaire
Python autoportant.

## Le calcul des tarifs moto / taxi

`services/recommendation-service/app/fare.py` calcule une estimation de
trajet entre deux lieux du catalogue :

1. Distance à vol d'oiseau (formule de Haversine) entre leurs coordonnées
   GPS réelles, majorée de 30 % pour approximer la distance réelle par la
   route.
2. Un tarif = prix de base + (prix au km × distance), avec un minimum,
   calibré sur le seul repère public fiable trouvé pour Bafoussam : la
   course de taxi partagé standard à ~350 FCFA en journée (Wikivoyage), et
   la course "dépôt" privée à 3 000-3 500 FCFA.

C'est explicitement une **estimation**, affichée comme telle dans
l'application — les transports urbains à Bafoussam sont négociés
informellement, il n'existe pas de grille tarifaire officielle à
reproduire.

Endpoint : `GET /fare?from_id=...&to_id=...&mode=moto|taxi` (voir la
documentation interactive sur http://localhost:8003/docs).

## Tests

Backend (45 tests au total, isolés avec SQLite — ni Postgres ni RabbitMQ
requis) :

```bash
cd services/user-service            && pip install -r requirements.txt && pytest
cd ../itinerary-service              && pip install -r requirements.txt && pytest
cd ../recommendation-service         && pip install -r requirements.txt && pytest
cd ../../gateway                     && pip install -r requirements.txt && pytest
```

Frontend (33 tests Vitest) :

```bash
cd frontend
npm install
npm test
```

## Dépannage

**Le frontend affiche "Cannot reach the server" / erreurs réseau**
Vérifiez que `docker compose ps` (ou vos 4 terminaux manuels) montrent bien
le gateway comme actif sur le port 8000, et que `frontend/.env` (ou
`VITE_API_BASE_URL` au build) pointe bien vers `http://localhost:8000`. Si
vous avez modifié le port du gateway, il faut **reconstruire** le frontend
(`npm run build` ou `docker compose build frontend`) car cette variable est
figée au moment du build, pas lue au runtime.

**`GET /health` sur le gateway indique un service "unreachable"**
Ce service met probablement encore un peu de temps à démarrer, ou n'a pas pu
se connecter à Postgres/RabbitMQ. Regardez ses logs :
`docker compose logs user-service` (ou le service concerné).

**Erreur Postgres "role does not exist" ou "password authentication failed"**
Vérifiez que `POSTGRES_USER`/`POSTGRES_PASSWORD` dans `.env` correspondent
bien à ce que vous utilisez, et que vous êtes reparti d'un volume propre si
vous avez changé ces valeurs après un premier lancement :
`docker compose down -v` puis `docker compose up --build`.

**Les images des lieux ne s'affichent pas**
Elles sont chargées en direct depuis Wikimedia Commons — une coupure
réseau ou un pare-feu bloquant `commons.wikimedia.org` les empêchera de
s'afficher (le reste de l'application continue de fonctionner normalement).
