import axios from 'axios'
import { API_BASE_URL } from '../config'
import { authStore } from '../stores/auth'
import { toastStore } from '../stores/toast'
import router from '../router'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

// Attach the JWT to every outgoing request automatically.
client.interceptors.request.use((config) => {
  if (authStore.state.token) {
    config.headers.Authorization = `Bearer ${authStore.state.token}`
  }
  return config
})

// Turn every HTTP error into a readable toast, and bounce expired
// sessions back to the login page.
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    const message = readableDetail(detail)

    if (status === 401) {
      const wasAuthed = authStore.isAuthenticated()
      authStore.clearSession()
      if (wasAuthed) {
        toastStore.error(message || 'Your session expired — please sign in again.')
        router.push({ name: 'login' })
      } else {
        toastStore.error(message || 'Incorrect username or password.')
      }
    } else if (status === 409) {
      toastStore.error(message || 'That already exists.')
    } else if (status === 404) {
      toastStore.error(message || "We couldn't find that.")
    } else if (status === 422) {
      toastStore.error(message || 'Please check the form and try again.')
    } else if (status === 400) {
      toastStore.error(message || 'That request could not be completed.')
    } else if (!error.response) {
      toastStore.error('Cannot reach the server. Is the API running?')
    } else {
      toastStore.error(message || 'Something went wrong. Please try again.')
    }

    return Promise.reject(error)
  }
)

function readableDetail(detail) {
  if (!detail) return null
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : null
        const msg = d.msg || 'Invalid value'
        return field ? `${field}: ${msg}` : msg
      })
      .join(' · ')
  }
  return null
}

export default client
