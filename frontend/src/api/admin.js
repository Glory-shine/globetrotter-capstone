import client from './client'

export function getUserStats() {
  return client.get('/users/admin/stats').then((r) => r.data)
}

export function getItineraryStats() {
  return client.get('/itineraries/admin/stats').then((r) => r.data)
}
