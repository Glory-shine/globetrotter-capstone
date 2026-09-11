# GlobeTrotter Bafoussam — Frontend

Application Vue 3 + Vite + Tailwind CSS. Pour le guide complet (backend +
frontend + Docker), voir le **README à la racine du projet**. Ce document
couvre les spécificités du frontend seul.

## Démarrage

```bash
npm install
cp .env.example .env    # VITE_API_BASE_URL=http://localhost:8000 par défaut
npm run dev              # http://localhost:5173
```

Le gateway backend (voir README racine) doit tourner sur le port indiqué
par `VITE_API_BASE_URL` pour que l'application fonctionne.

## Identité visuelle

Palette inspirée des motifs Bamiléké : rouge terracotta (`--color-sage`),
indigo nuit (`--color-deep-blue`), or raffia (`--color-lavender`), et
canevas crème de marché (`--color-cream`) — tokens définis dans
`src/assets/main.css`, réutilisés automatiquement par tous les composants.
Un dégradé de triangles (`.bamileke-band`) rappelant les tissus ndop sert
de séparateur décoratif sur les pages principales.

Typographies : Fraunces (titres), Plus Jakarta Sans (texte), JetBrains
Mono (données/prix/coordonnées).

## Fonctionnalités clés

- **Carte réelle** (`InteractiveMap.vue`) — Leaflet + tuiles OpenStreetMap,
  coordonnées GPS réelles de chaque lieu de Bafoussam
- **Calculateur de tarif** (`FareCalculator.vue`) — estimation moto-taxi ou
  taxi entre deux lieux, via `GET /fare` sur le backend
- **Fiches lieux** (`DestinationCard.vue`, `DestinationDetailsView.vue`) —
  photos réelles, catégorie, note, activités avec leur prix en FCFA
- Recherche/filtres par commune, tag, budget (`DashboardView.vue`)
- Authentification JWT, itinéraires, recommandations personnalisées

## Structure

```
src/
├── config.js              # API_BASE_URL, tags, centre de Bafoussam
├── router.js                # Routes + garde d'authentification
├── api/                     # register/login, destinations, recommendations, itineraries, fare
├── stores/                   # auth, toast, cache des destinations
├── components/                # DestinationCard, FareCalculator, InteractiveMap, ItineraryForm…
└── views/                      # Login, Register, Dashboard, DestinationDetails, Itineraries…
tests/                        # Vitest + @vue/test-utils
```

## Tests

```bash
npm test
```

## Build & Docker

```bash
npm run build       # sortie dans dist/
npm run preview     # tester le build en local
```

Un `Dockerfile` (build multi-étapes Node → Nginx) et un `nginx.conf` sont
fournis pour le déploiement conteneurisé — voir le `docker-compose.yml` à
la racine, qui construit et lance ce service automatiquement.

> Note : `VITE_API_BASE_URL` est figée **au moment du build** (limitation
> de Vite), pas lue au démarrage du conteneur. Pour changer l'URL du
> gateway en Docker, reconstruisez l'image avec
> `docker compose build --build-arg VITE_API_BASE_URL=... frontend` ou la
> variable d'environnement `FRONTEND_API_BASE_URL` du `.env` racine.
