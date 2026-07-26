# Spécifications et Exigences — GlobeTrotter

## 1. Objectif du système

GlobeTrotter est un système de recommandation et de planification de voyages destiné à aider un utilisateur à :
- découvrir des destinations,
- filtrer des propositions selon ses préférences,
- obtenir des recommandations personnalisées,
- créer et consulter des itinéraires de voyage.

Le système est composé d’un backend API REST basé sur FastAPI et d’un frontend web basé sur Vue.js.

---

## 2. Périmètre fonctionnel

### 2.1 Fonctionnalités couvertes

Le système permet de :
1. créer un compte utilisateur,
2. authentifier un utilisateur via un jeton JWT,
3. rechercher des destinations avec filtres,
4. afficher des destinations par catégories et tags,
5. proposer des recommandations personnalisées,
6. créer un itinéraire de voyage,
7. consulter les itinéraires associés à un utilisateur,
8. valider les données saisies,
9. fournir un retour utilisateur clair en cas d’erreur.

### 2.2 Fonctionnalités non couvertes dans la version actuelle

- paiement ou réservation de voyages,
- intégration avec des APIs externes de voyages,
- gestion d’administration avancée,
- partage social des itinéraires,
- notifications push ou email.

---

## 3. Spécifications fonctionnelles

### FR-01 — Inscription utilisateur
Le système doit permettre à un visiteur de créer un compte avec :
- un nom d’utilisateur,
- une adresse e-mail,
- un mot de passe,
- une liste de préférences optionnelle.

Le système doit refuser l’inscription si :
- le nom d’utilisateur existe déjà,
- l’e-mail est déjà utilisé,
- les données ne respectent pas les contraintes de validation.

### FR-02 — Authentification utilisateur
Le système doit permettre à un utilisateur enregistré de se connecter avec ses identifiants.

Le système doit retourner un jeton d’accès si l’authentification réussit, et un message d’erreur si elle échoue.

### FR-03 — Protection d’accès
Les routes sensibles doivent être accessibles uniquement aux utilisateurs authentifiés.

Les utilisateurs non authentifiés doivent être redirigés vers la page de connexion.

### FR-04 — Recherche de destinations
Le système doit permettre la recherche de destinations via :
- un mot-clé libre,
- un filtre par pays,
- un filtre par tag,
- un filtre par budget maximum.

Les résultats doivent être renvoyés sous forme de liste structurée.

### FR-05 — Filtrage par catégorie
Le système doit permettre de filtrer les destinations selon des catégories telles que :
- culture,
- nature,
- gastronomie,
- nightlife.

Le filtrage peut s’appuyer sur les tags et la catégorie associés aux destinations.

### FR-06 — Affichage détaillé des destinations
Chaque destination doit afficher au minimum :
- le nom,
- le pays,
- les tags,
- la description,
- le coût moyen par jour,
- la catégorie,
- la météo/climat,
- la saison recommandée.

### FR-07 — Recommandations personnalisées
Le système doit proposer des destinations adaptées aux préférences de l’utilisateur, à son budget et à ses itinéraires précédents.

La logique de recommandation doit être stable, cohérente et limitée par un nombre maximum demandé par l’utilisateur.

### FR-08 — Création d’itinéraire
Le système doit permettre à un utilisateur authentifié de créer un itinéraire comprenant :
- un titre,
- une destination,
- une date de début,
- une date de fin,
- une liste d’activités par jour.

L’itinéraire doit être associé à l’utilisateur connecté.

### FR-09 — Consultation des itinéraires
Le système doit permettre à un utilisateur de consulter uniquement ses propres itinéraires.

### FR-10 — Validation des itinéraires
Le système doit valider les données d’itinéraire avant enregistrement.

Les règles de validation doivent inclure :
- date de fin supérieure ou égale à la date de début,
- day ≥ 1,
- activité non vide et de longueur limitée.

### FR-11 — Gestion des erreurs
Le système doit fournir des réponses claires et compréhensibles en cas :
- d’erreur de validation,
- d’erreur métier,
- de problème réseau,
- d’authentification refusée.

### FR-12 — Santé du système
Le système doit exposer un point de contrôle de santé accessible via une route dédiée.

---

## 4. Exigences fonctionnelles détaillées

| ID | Exigence | Priorité |
|---|---|---|
| FR-01 | Inscription utilisateur avec validation | Haute |
| FR-02 | Authentification robuste via jeton JWT | Haute |
| FR-03 | Protection des routes privées | Haute |
| FR-04 | Recherche avancée de destinations | Haute |
| FR-05 | Filtrage par catégorie et tags | Moyenne |
| FR-06 | Affichage complet des informations de destination | Haute |
| FR-07 | Recommandations personnalisées | Moyenne |
| FR-08 | Création d’itinéraires | Haute |
| FR-09 | Consultation des itinéraires personnels | Haute |
| FR-10 | Validation des données saisies | Haute |
| FR-11 | Gestion et affichage des erreurs | Haute |
| FR-12 | Endpoint de santé du système | Faible |

---

## 5. Exigences non fonctionnelles

### NFR-01 — Sécurité
Le système doit protéger les données sensibles et empêcher tout accès non autorisé aux ressources privées.

Exigences :
- utilisation de JWT pour l’authentification,
- stockage sécurisé des mots de passe via hachage,
- accès limité aux données utilisateur à l’utilisateur concerné.

### NFR-02 — Fiabilité
Le système doit fonctionner de manière stable même en cas d’erreurs de saisie ou de requêtes concurrentes.

Exigences :
- les erreurs doivent être gérées proprement,
- les écritures de données doivent être atomiques,
- les opérations critiques doivent éviter la corruption de données.

### NFR-03 — Performance
Le système doit répondre rapidement aux opérations courantes de recherche et de consultation.

Exigences :
- temps de réponse raisonnable pour la recherche et les requêtes API,
- chargement fluide des écrans dans l’interface utilisateur,
- utilisation de mécanismes de filtrage et de pagination logique adaptée.

### NFR-04 — Utilisabilité
L’interface doit être claire, intuitive et facile à utiliser pour un utilisateur non technique.

Exigences :
- formulaires simples,
- messages d’erreur explicites,
- feedback visuel pendant les opérations de chargement.

### NFR-05 — Compatibilité
Le système doit être compatible avec les navigateurs modernes et les clients HTTP standard.

Exigences :
- interface web compatible avec les navigateurs récents,
- API fonctionnant avec des clients REST standards,
- support de la plateforme Windows/Linux/macOS pour le backend et le frontend.

### NFR-06 — Maintenabilité
Le code doit être structuré de manière claire et modulaire.

Exigences :
- séparation des responsabilités entre API, logique métier et stockage,
- code documenté et testable,
- tests automatisés pour les fonctionnalités principales.

### NFR-07 — Extensibilité
Le système doit permettre l’ajout de nouvelles fonctionnalités sans refonte complète.

Exigences :
- architecture modulaire,
- logique métier isolée,
- ajout facile de nouveaux modules de recommandation ou de destinations.

### NFR-08 — Portabilité
Le système doit pouvoir être déployé sur plusieurs environnements de développement et de production.

Exigences :
- configuration via variables d’environnement,
- exécution possible localement et en environnement conteneurisé ou serveur simple.

---

## 6. Règles métier

- Une destination doit être identifiable de manière unique.
- Un utilisateur ne peut voir que ses propres itinéraires.
- Une inscription avec un e-mail ou un nom d’utilisateur déjà utilisé est refusée.
- Une date de fin d’itinéraire ne peut pas être antérieure à la date de début.
- Les activités d’un itinéraire doivent être renseignées avec des données valides.

---

## 7. Contraintes techniques

- Backend : FastAPI.
- Frontend : Vue.js avec Vite.
- Authentification : JWT.
- Stockage : fichier JSON local (version actuelle).
- Tests : pytest pour le backend, Vitest pour le frontend.

---

## 8. Hypothèses et dépendances

- Le backend et le frontend sont exécutés sur des hôtes distincts ou localement dans un environnement de développement.
- Le stockage JSON est suffisant pour la version actuelle du système.
- Les données de destinations sont fournies sous forme de catalogue local.

---

## 9. Résumé

GlobeTrotter est un système de voyage orienté utilisateur, centré sur la découverte, la personnalisation et la planification. Les exigences fonctionnelles et non fonctionnelles définies ici couvrent les besoins essentiels du produit actuel ainsi que la base d’une évolution future vers une plateforme plus riche et plus robuste.
