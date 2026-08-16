import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const mockComment = {
  id: 'c1',
  destination_id: 'dest-001',
  parent_id: null,
  user_id: 'user-999',
  username: 'kofi',
  text: 'Superbe lieu, à visiter absolument.',
  likes_count: 2,
  liked_by_me: false,
  created_at: new Date().toISOString(),
  replies: [],
}

const listComments = vi.fn(() => Promise.resolve([mockComment]))
const createComment = vi.fn((destinationId, { text, parentId }) =>
  Promise.resolve({
    id: 'c2',
    destination_id: destinationId,
    parent_id: parentId || null,
    user_id: 'user-123',
    username: 'traveler1',
    text,
    likes_count: 0,
    liked_by_me: false,
    created_at: new Date().toISOString(),
    replies: [],
  })
)
const toggleCommentLike = vi.fn((commentId) =>
  Promise.resolve({ ...mockComment, id: commentId, likes_count: 3, liked_by_me: true })
)

vi.mock('../src/api/comments', () => ({
  listComments: (...args) => listComments(...args),
  createComment: (...args) => createComment(...args),
  toggleCommentLike: (...args) => toggleCommentLike(...args),
}))

import CommentSection from '../src/components/CommentSection.vue'

describe('CommentSection', () => {
  beforeEach(() => {
    listComments.mockClear()
    createComment.mockClear()
    toggleCommentLike.mockClear()
  })

  it('loads and renders existing comments for the destination', async () => {
    const wrapper = mount(CommentSection, { props: { destinationId: 'dest-001' } })
    await flushPromises()

    expect(listComments).toHaveBeenCalledWith('dest-001')
    expect(wrapper.text()).toContain('kofi')
    expect(wrapper.text()).toContain('Superbe lieu, à visiter absolument.')
  })

  it('posts a new top-level comment and prepends it to the list', async () => {
    const wrapper = mount(CommentSection, { props: { destinationId: 'dest-001' } })
    await flushPromises()

    await wrapper.find('textarea').setValue('Mon avis sur ce lieu')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createComment).toHaveBeenCalledWith('dest-001', { text: 'Mon avis sur ce lieu', parentId: undefined })
    expect(wrapper.text()).toContain('Mon avis sur ce lieu')
  })

  it('toggles a like on a comment', async () => {
    const wrapper = mount(CommentSection, { props: { destinationId: 'dest-001' } })
    await flushPromises()

    const likeButton = wrapper.findAll('button').find((b) => b.text().includes('2'))
    await likeButton.trigger('click')
    await flushPromises()

    expect(toggleCommentLike).toHaveBeenCalledWith('c1')
    expect(wrapper.text()).toContain('3')
  })

  it('shows an empty state when there are no comments', async () => {
    listComments.mockResolvedValueOnce([])
    const wrapper = mount(CommentSection, { props: { destinationId: 'dest-002' } })
    await flushPromises()

    expect(wrapper.text()).toContain('Aucun avis pour l\'instant')
  })
})
