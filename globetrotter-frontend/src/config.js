// Single source of truth for the backend location. Override at build/run
// time with a .env file (VITE_API_BASE_URL=...) — see .env.example.
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// Fixed tag vocabulary shared with the backend's mock destination data —
// used to render preference/filter chips consistently across the app.
export const PREFERENCE_TAGS = [
  'beach',
  'culture',
  'mountain',
  'adventure',
  'budget',
  'romantic',
  'food',
  'nightlife',
  'nature',
  'wildlife',
  'history',
  'family',
]

export const CATEGORY_EMOJIS = {
  all: '🗺️',
  food: '🍽️',
  culture: '🏛️',
  nature: '🌳',
  nightlife: '🌙',
}
