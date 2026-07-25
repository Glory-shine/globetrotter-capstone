import client from './client'

export function createItinerary(payload) {
  return client.post('/itineraries', payload).then((r) => r.data)
}

export function listItineraries() {
  return client.get('/itineraries').then((r) => r.data)
}
