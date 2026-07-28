# GlobeTrotter Frontend System Overview

Ce document décrit le fonctionnement du dossier `globetrotter-frontend`, son architecture, ses flux de données, et son intégration avec le backend FastAPI.

## 1. Vue d'ensemble

`globetrotter-frontend` est une application Vue 3 construite avec Vite. Elle fonctionne comme une Single Page Application (SPA) qui se connecte à une API REST distante pour l'authentification, la recherche de destinations, les recommandations et la gestion des itinéraires.

### Principaux objectifs

- Authentifier l'utilisateur avec un JWT
- Consommer l'API backend via Axios
- Afficher une liste de destinations filtrables
- Fournir une page de détail de destination avec carte
- Permettre à l'utilisateur de consulter des recommandations et de planifier des itinéraires
- Gérer les erreurs et afficher des notifications toast globales

## 2. Installation et démarrage

Requis : Node 18+.

```bash
npm install
npm run dev
```

Le projet est prêt à fonctionner sur `http://localhost:5173`.

### Configuration de l'API

- `src/config.js` définit `API_BASE_URL`.
- Par défaut, l'application utilise `https://globetrotter-travelassistant-production.up.railway.app`.
- Pour pointer vers un autre backend, copier `.env.example` vers `.env` et définir `VITE_API_BASE_URL`.

## 3. Structure du projet

```
src/
├── api/                 # couche HTTP Axios vers le backend
├── components/          # composants réutilisables UI
├── stores/              # état global minimal (auth, cache, toast)
├── views/               # pages par route
├── router.js            # définition des routes et garde d'accès
├── config.js            # configuration globale
├── App.vue              # wrapper principal + ToastContainer
└── main.js              # montage de Vue + router
```

## 4. Entrée de l’application

- `src/main.js` monte l'application Vue et injecte le routeur.
- `src/App.vue` contient la barre de navigation (`NavBar`), la zone de rendu des vues (`router-view`) et le conteneur de toasts (`ToastContainer`).

## 5. Routing et protection des pages

- `src/router.js` définit les routes principales :
  - `/login`
  - `/register`
  - `/destinations`
  - `/destinations/:id`
  - `/profile`
  - `/recommendations`
  - `/itineraries`

- Chaque route protégée utilise `meta.requiresAuth`.
- Le garde `beforeEach` vérifie si l'utilisateur est authentifié via `authStore.isAuthenticated()`.
- Si l'utilisateur n'est pas connecté, il est redirigé vers `/login`.
- Les pages `login` et `register` sont réservées aux visiteurs non connectés.

## 6. Gestion de l’authentification

### Store d'authentification

- `src/stores/auth.js` stocke :
  - `token` JWT
  - `username`
  - `preferences`

- Ces valeurs sont persistées dans `localStorage` avec les clés :
  - `globetrotter_token`
  - `globetrotter_username`
  - `globetrotter_preferences`

- Fonctions principales :
  - `setSession()` : enregistre token, nom d'utilisateur et préférences
  - `clearSession()` : supprime la session et vide le stockage
  - `isAuthenticated()` : retourne `true` si un token existe

### Flux de connexion / inscription

- `src/api/auth.js` expose :
  - `register()` pour `POST /register`
  - `login()` pour `POST /login`

- Après authentification réussie, l'application stocke le JWT et les informations utilisateur.
- Le token est automatiquement attaché à chaque requête API suivante.

## 7. Couche API HTTP

### Axios et gestion des erreurs

- `src/api/client.js` crée une instance Axios commune.
- Un intercepteur de requête ajoute le header `Authorization: Bearer <token>` si l'utilisateur est connecté.
- Un intercepteur de réponse gère les erreurs globales :
  - 401 : session expirée ou utilisateur non authentifié
  - 409 : conflit de ressource
  - 404 : ressource non trouvée
  - 422 : validation de payload
  - problèmes de réseau

- Les erreurs sont converties en messages lisibles, puis affichées via le store de toasts.

### Services API

- `src/api/destinations.js`
  - `searchDestinations({ q, tag, country, max_cost })`
  - Appelle `GET /destinations`
- `src/api/recommendations.js`
  - `getRecommendations({ limit, max_budget })`
  - Appelle `GET /recommendations`
- `src/api/itineraries.js`
  - `createItinerary(payload)`
  - `listItineraries()`
  - `updateItinerary(itineraryId, payload)`
  - `deleteItinerary(itineraryId)`
- `src/api/auth.js`
  - `register()`
  - `login()`

## 8. État global et cache

### `destinationsCache`

- `src/stores/destinationsCache.js` garde un cache local des destinations par `id`.
- Permet de réutiliser les données déjà chargées sans rappeler le backend immédiatement.
- Utile pour afficher rapidement une destination dans `DestinationDetailsView`.

### `toastStore`

- `src/stores/toast.js` gère la file de notifications.
- Offre des helpers : `success()`, `error()`, `info()`.
- Les toasts disparaissent automatiquement après un délai.

## 9. Pages principales

### `DashboardView.vue`

- Page d’accueil après connexion.
- Propose : recherche textuelle, filtre par tag, budget journalier, et tri par catégorie.
- Charge les destinations via `searchDestinations()`.
- Met en cache les résultats via `destinationsCache.cache(data)`.
- Affiche soit une liste de cartes `DestinationCard`, soit un mode carte via `InteractiveMap`.
- Permet de planifier un voyage en redirigeant vers `/itineraries`.

### `DestinationDetailsView.vue`

- Affiche le détail d’une destination unique.
- Récupère l’ID depuis `route.params.id`.
- Cherche d’abord dans `destinationsCache`; si absent, recharge toutes les destinations depuis l’API.
- Montre la description, les médias, les activités et une carte interactive.
- Offre un bouton de retour pour revenir à la page précédente.

### Autres vues

- `ProfileView.vue` : gère le profil utilisateur et ses préférences
- `RecommendationsView.vue` : affiche des recommandations personnalisées du backend
- `ItinerariesView.vue` : liste et gère les itinéraires de l’utilisateur
- `LoginView.vue` / `RegisterView.vue` : formulaires de connexion et d’inscription

## 10. Composants réutilisables

### `DestinationCard.vue`

- Affiche un résumé de destination avec :
  - nom, pays, description, tags, likes, climat, saison
- Propose deux actions : `Plan a trip` et `Details`.
- Émet un événement `plan` pour démarrer la création d’un itinéraire.

### `InteractiveMap.vue`

- Composant de carte réutilisable utilisé dans le dashboard et la page de détail.
- Affiche des points de destination et un centre de carte.
- Supporte un mode compact pour ne pas prendre trop de place dans `DestinationDetailsView`.

### `ToastContainer.vue`

- Rend les messages de `toastStore`.
- Les notifications restent visibles quelques secondes puis disparaissent.

## 11. Flux utilisateur clé

1. L’utilisateur arrive sur `/login` ou `/register`.
2. Il soumet ses identifiants.
3. Le backend renvoie un JWT.
4. Le frontend garde le JWT en `localStorage`.
5. Les requêtes suivantes envoient ce JWT automatiquement.
6. L’utilisateur peut rechercher des destinations et naviguer vers un détail.
7. Les actions de backend réussies et les erreurs sont affichées via des toasts.

## 12. Tests et build

- `npm test` lance les tests existants avec Vitest.
- `npm run build` produit la version de production dans `dist/`.
- `npm run preview` sert le build localement.

## 13. Points importants

- Le frontend est découplé du backend : il consomme uniquement une API REST.
- `router.js` impose la protection des vues et gère la redirection en fonction du statut de connexion.
- `authStore` et `client.js` sont les cœurs de l’authentification.
- `destinationsCache` améliore la fluidité des pages de détail en évitant des appels API redondants.
- Le design est centré sur l’expérience voyage : cartes, filtres de destination et itinéraires.
