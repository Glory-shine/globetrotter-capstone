import client from './client'

export function getRecommendations({ limit, max_budget } = {}) {
  const params = {}
  if (limit) params.limit = limit
  if (max_budget !== null && max_budget !== undefined && max_budget !== '') {
    params.max_budget = max_budget
  }

  return client.get('/recommendations', { params }).then((r) => r.data)
}
