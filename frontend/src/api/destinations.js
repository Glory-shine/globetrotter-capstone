import client from './client'

export function searchDestinations({ q, tag, country, max_cost } = {}) {
  const params = {}
  if (q) params.q = q
  if (tag) params.tag = tag
  if (country) params.country = country
  if (max_cost !== null && max_cost !== undefined && max_cost !== '') params.max_cost = max_cost

  return client.get('/destinations', { params }).then((r) => r.data)
}

export function getDestination(id) {
  return client.get(`/destinations/${id}`).then((r) => r.data)
}

export function toggleFavorite(id) {
  return client.post(`/destinations/${id}/favorite`).then((r) => r.data)
}

export function listFavorites() {
  return client.get('/favorites').then((r) => r.data)
}

export function createDestination(payload) {
  return client.post('/destinations', payload).then((r) => r.data)
}

export function getDestinationStats() {
  return client.get('/destinations/admin/stats').then((r) => r.data)
}
