import client from './client'

export function listComments(destinationId) {
  return client.get(`/destinations/${destinationId}/comments`).then((r) => r.data)
}

export function createComment(destinationId, { text, parentId }) {
  return client
    .post(`/destinations/${destinationId}/comments`, { text, parent_id: parentId || null })
    .then((r) => r.data)
}

export function toggleCommentLike(commentId) {
  return client.post(`/comments/${commentId}/like`).then((r) => r.data)
}

export function listMyComments() {
  return client.get('/comments/mine').then((r) => r.data)
}
