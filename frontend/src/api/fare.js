import client from './client'

export function getFareEstimate({ fromId, toId, mode }) {
  return client
    .get('/fare', { params: { from_id: fromId, to_id: toId, mode } })
    .then((r) => r.data)
}
