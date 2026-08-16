import { reactive, readonly } from 'vue'

const TOKEN_KEY = 'globetrotter_token'
const USERNAME_KEY = 'globetrotter_username'
const PREFERENCES_KEY = 'globetrotter_preferences'
const AVATAR_KEY = 'globetrotter_avatar'
const ROLE_KEY = 'globetrotter_role'

const state = reactive({
  token: localStorage.getItem(TOKEN_KEY) || null,
  username: localStorage.getItem(USERNAME_KEY) || null,
  preferences: JSON.parse(localStorage.getItem(PREFERENCES_KEY) || '[]'),
  avatar: localStorage.getItem(AVATAR_KEY) || null,
  role: localStorage.getItem(ROLE_KEY) || 'user',
})

function setSession({ token, username, preferences = [], role }) {
  state.token = token
  state.username = username || null
  state.preferences = preferences
  // role is only sent by login/register; profile updates that re-call
  // setSession without it must not silently downgrade the current role.
  if (role) state.role = role

  localStorage.setItem(TOKEN_KEY, token)
  if (username) localStorage.setItem(USERNAME_KEY, username)
  localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences))
  if (role) localStorage.setItem(ROLE_KEY, role)
}

function setAvatar(dataUrl) {
  state.avatar = dataUrl || null
  if (dataUrl) {
    localStorage.setItem(AVATAR_KEY, dataUrl)
  } else {
    localStorage.removeItem(AVATAR_KEY)
  }
}

function clearSession() {
  state.token = null
  state.username = null
  state.preferences = []
  state.avatar = null
  state.role = 'user'
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USERNAME_KEY)
  localStorage.removeItem(PREFERENCES_KEY)
  localStorage.removeItem(AVATAR_KEY)
  localStorage.removeItem(ROLE_KEY)
}

function isAuthenticated() {
  return !!state.token
}

function isAdmin() {
  return state.role === 'admin'
}

export const authStore = {
  state: readonly(state),
  setSession,
  setAvatar,
  clearSession,
  isAuthenticated,
  isAdmin,
}
