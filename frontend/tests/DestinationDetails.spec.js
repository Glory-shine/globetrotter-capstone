import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock vue-router to provide route params and router access. Also stub
// createRouter/createWebHistory: src/api/client.js transitively imports
// src/router.js (for redirect-to-login on 401), which calls createRouter
// at module load time.
vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: 'dest-001' } }),
  useRouter: () => ({ back: vi.fn(), push: vi.fn() }),
  createRouter: () => ({ beforeEach: vi.fn(), push: vi.fn() }),
  createWebHistory: () => ({}),
}))

const mockDestination = {
  id: 'dest-001',
  name: 'Chefferie Supérieure de Bafoussam',
  country: 'Bafoussam I (Centre-ville)',
  category: 'Chefferie',
  tags: ['chefferie', 'culture'],
  latitude: 5.474,
  longitude: 10.413,
  rating: 4.7,
  price_range_xaf: '2 000 - 5 000 FCFA',
  description: 'Résidence du chef supérieur des Bafoussam.',
  best_season: "Toute l'année",
  avg_cost_per_day: 2000,
  media: {
    main: 'https://commons.wikimedia.org/wiki/Special:FilePath/example.jpg',
    secondary: ['https://commons.wikimedia.org/wiki/Special:FilePath/example2.jpg'],
  },
  activities: [
    { name: 'Visite guidée du palais royal', price: '2 000 FCFA' },
    { name: 'Visite avec accès à la forêt sacrée', price: '5 000 FCFA' },
  ],
}

const mockOtherDestination = {
  id: 'dest-005',
  name: 'Marché A (Grand Marché de Bafoussam)',
  latitude: 5.477,
  longitude: 10.42,
}

vi.mock('../src/api/destinations', () => ({
  searchDestinations: vi.fn(() => Promise.resolve([mockDestination, mockOtherDestination])),
  toggleFavorite: vi.fn((id) => Promise.resolve({ id, is_favorite: true })),
}))

// Stub the InteractiveMap to avoid a real Leaflet dependency in tests
const InteractiveMapStub = {
  name: 'InteractiveMap',
  props: ['items', 'center', 'visible', 'title', 'showUserLocation'],
  template: '<div class="interactive-map-stub">map</div>',
}

import DestinationDetailsView from '../src/views/DestinationDetailsView.vue'

describe('DestinationDetailsView', () => {
  it('renders destination details fetched from the API/cache', async () => {
    const wrapper = mount(DestinationDetailsView, {
      global: {
        components: { InteractiveMap: InteractiveMapStub },
      },
    })

    await new Promise((r) => setTimeout(r, 0))
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Chefferie Supérieure de Bafoussam')
    expect(wrapper.text()).toContain('Résidence du chef supérieur des Bafoussam.')
    expect(wrapper.text()).toContain('Chefferie')

    // main media shown via img src
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe(mockDestination.media.main)

    // priced activities
    expect(wrapper.text()).toContain('Visite guidée du palais royal')
    expect(wrapper.text()).toContain('2 000 FCFA')

    // real coordinates
    expect(wrapper.text()).toContain('5.47400')
    expect(wrapper.text()).toContain('10.41300')
    expect(wrapper.findComponent(InteractiveMapStub).props('showUserLocation')).toBe(false)

    // fare calculator widget is present with the other destination as an origin option
    expect(wrapper.text()).toContain("Comment s'y rendre")
    expect(wrapper.text()).toContain('Marché A (Grand Marché de Bafoussam)')
  })
})
