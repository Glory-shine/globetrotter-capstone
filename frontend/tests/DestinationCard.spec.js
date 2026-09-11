import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const toggleFavorite = vi.fn((id) => Promise.resolve({ id, is_favorite: true }))

vi.mock('../src/api/destinations', () => ({
  toggleFavorite: (...args) => toggleFavorite(...args),
}))

import DestinationCard from '../src/components/DestinationCard.vue'

const mockDestination = {
  id: 'dest-001',
  name: 'Chefferie Supérieure de Bafoussam',
  country: 'Bafoussam I (Centre-ville)',
  category: 'Chefferie',
  tags: ['chefferie', 'culture', 'histoire'],
  avg_cost_per_day: 2000,
  rating: 4.7,
  price_range_xaf: '2 000 - 5 000 FCFA',
  description: 'Résidence du chef supérieur des Bafoussam.',
  best_season: "Toute l'année",
  media: { main: '', secondary: [] },
}

describe('DestinationCard', () => {
  it('renders the destination name, commune, and description from mock JSON', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })

    expect(wrapper.text()).toContain('Chefferie Supérieure de Bafoussam')
    expect(wrapper.text()).toContain('Bafoussam I (Centre-ville)')
    expect(wrapper.text()).toContain('Résidence du chef supérieur des Bafoussam.')
  })

  it('renders every tag from the mock data', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })

    for (const tag of mockDestination.tags) {
      expect(wrapper.text().toLowerCase()).toContain(tag)
    }
  })

  it('shows the FCFA price range and rating in the stub', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    expect(wrapper.text()).toContain('2 000 - 5 000 FCFA')
    expect(wrapper.text()).toContain('4.7')
  })

  it('shows "Gratuit" when there is no price range and the entry fee is zero', () => {
    const wrapper = mount(DestinationCard, {
      props: { destination: { ...mockDestination, price_range_xaf: '', avg_cost_per_day: 0 } },
    })
    expect(wrapper.text()).toContain('Gratuit')
  })

  it('renders a destination image from backend-provided media', () => {
    const wrapper = mount(DestinationCard, {
      props: {
        destination: {
          ...mockDestination,
          media: { main: 'https://commons.wikimedia.org/wiki/Special:FilePath/example.jpg' },
        },
      },
    })

    const image = wrapper.find('img[alt="Photo de Chefferie Supérieure de Bafoussam"]')
    expect(image.exists()).toBe(true)
    expect(image.attributes('src')).toContain('Special:FilePath/example.jpg')
  })

  it('shows a "Pour vous" stamp only when matchTags overlap the destination tags', () => {
    const noMatch = mount(DestinationCard, { props: { destination: mockDestination } })
    expect(noMatch.text()).not.toContain('Pour vous')

    const withMatch = mount(DestinationCard, {
      props: { destination: mockDestination, matchTags: ['chefferie'] },
    })
    expect(withMatch.text()).toContain('Pour vous')
  })

  it('emits "plan" with the destination when the CTA is clicked', async () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    const planButton = wrapper.findAll('button').find((button) => button.text() === 'Planifier')

    expect(planButton).toBeTruthy()
    await planButton.trigger('click')

    expect(wrapper.emitted('plan')).toHaveLength(1)
    expect(wrapper.emitted('plan')[0][0]).toEqual(mockDestination)
  })

  it('shows a Détails button on the card', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThanOrEqual(2)
    expect(wrapper.text()).toContain('Détails')
  })

  it('toggles the favorite/like button via the API and reflects the new state', async () => {
    const wrapper = mount(DestinationCard, { props: { destination: { ...mockDestination, is_favorite: false } } })

    expect(wrapper.text()).toContain('♡')
    await wrapper.find('button[aria-label="Ajouter aux favoris"]').trigger('click')
    await flushPromises()

    expect(toggleFavorite).toHaveBeenCalledWith('dest-001')
    expect(wrapper.text()).toContain('♥')
  })
})
