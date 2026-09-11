import client from './client'

export function register({ username, email, password, preferences }) {
  return client.post('/register', { username, email, password, preferences }).then((r) => r.data)
}

export function login({ username, password }) {
  return client.post('/login', { username, password }).then((r) => r.data)
}
