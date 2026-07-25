import { reactive, readonly } from 'vue'

const TOKEN_KEY = 'globetrotter_token'
const USERNAME_KEY = 'globetrotter_username'
const PREFERENCES_KEY = 'globetrotter_preferences'

const state = reactive({
  token: localStorage.getItem(TOKEN_KEY) || null,
  username: localStorage.getItem(USERNAME_KEY) || null,
  preferences: JSON.parse(localStorage.getItem(PREFERENCES_KEY) || '[]'),
})

function setSession({ token, username, preferences = [] }) {
  state.token = token
  state.username = username || null
  state.preferences = preferences

  localStorage.setItem(TOKEN_KEY, token)
  if (username) localStorage.setItem(USERNAME_KEY, username)
  localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences))
}

function clearSession() {
  state.token = null
  state.username = null
  state.preferences = []
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
  localStorage.removeItem(PREFERENCES_KEY)
}

function isAuthenticated() {
  return !!state.token
}

export const authStore = {
  state: readonly(state),
  setSession,
  clearSession,
  isAuthenticated,
}
