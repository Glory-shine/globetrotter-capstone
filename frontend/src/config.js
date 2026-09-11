// Single source of truth for the backend location. Override at build/run
// time with a .env file (VITE_API_BASE_URL=...) — see .env.example.
//
// Default points at the local API Gateway from the microservices backend
// (docker compose up, or the gateway run standalone) — see the root
// README for how to launch it. Point this at a deployed gateway URL for
// production.
const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
export const API_BASE_URL = configuredApiBaseUrl || 'http://localhost:8000'

// Tag vocabulary matching the Bafoussam catalog seeded by the
// recommendation-service — used to render preference/filter chips.
export const PREFERENCE_TAGS = [
  'chefferie',
  'culture',
  'marche',
  'artisanat',
  'nature',
  'religieux',
  'sport',
  'histoire',
  'famille',
  'aventure',
  'panorama',
  'gratuit',
]

export const CATEGORY_EMOJIS = {
  all: '🗺️',
  Chefferie: '👑',
  Musée: '🏛️',
  Marché: '🧺',
  Nature: '🌿',
  Monument: '🗿',
  Religieux: '⛪',
  Sport: '⚽',
  Transport: '🚌',
  Culture: '🥁',
  Hôtel: '🏨',
  Restaurant: '🍽️',
  Institution: '🏢',
  Hôpital: '🏥',
  Pharmacie: '💊',
  École: '🎒',
  Lycée: '🏫',
  Université: '🎓',
}

// Bafoussam's approximate city-center coordinates — used to default the
// interactive map view before any destination is selected.
export const BAFOUSSAM_CENTER = [5.4778, 10.4176]

// The three communes of the Communauté Urbaine de Bafoussam — used as the
// commune picker when an admin manually adds a destination.
export const COMMUNES = [
  'Bafoussam I (Centre-ville)',
  'Bafoussam II (Baleng)',
  'Bafoussam III (Bamougoum)',
]
