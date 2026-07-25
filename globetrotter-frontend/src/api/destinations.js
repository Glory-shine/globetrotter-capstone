import client from './client'

export function searchDestinations({ q, tag, country, max_cost } = {}) {
  const params = {}
  if (q) params.q = q
  if (tag) params.tag = tag
  if (country) params.country = country
  if (max_cost !== null && max_cost !== undefined && max_cost !== '') params.max_cost = max_cost

  return client.get('/destinations', { params }).then((r) => r.data)
}
