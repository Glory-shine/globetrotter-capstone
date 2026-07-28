import client from './client'

export function createItinerary(payload) {
  return client.post('/itineraries', payload).then((r) => r.data)
}

export function listItineraries() {
  return client.get('/itineraries').then((r) => r.data)
}

export function updateItinerary(itineraryId, payload) {
  return client.put(`/itineraries/${itineraryId}`, payload).then((r) => r.data)
}

export function deleteItinerary(itineraryId) {
  return client.delete(`/itineraries/${itineraryId}`)
}