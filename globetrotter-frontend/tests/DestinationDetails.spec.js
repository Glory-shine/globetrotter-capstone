import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'

// Mock vue-router useRoute to provide route params
vi.mock('vue-router', () => ({ useRoute: () => ({ params: { id: 'dest-001' } }) }))

// Mock the destinations API
const mockDestination = {
  id: 'dest-001',
  name: 'Mock Place',
  country: 'Mockland',
  tags: ['nature'],
  latitude: 1.23,
  longitude: 4.56,
  description: 'A lovely mock place',
  avg_cost_per_day: 100,
  media: {
    main: 'https://example.com/image.jpg',
    secondary: ['https://example.com/1.jpg', 'https://example.com/2.jpg'],
  },
  activities: [{ name: 'Guided tour', price: '$10' }, { name: 'Zoo entrance', price: '$5' }],
}

vi.mock('../src/api/destinations', () => ({
  searchDestinations: vi.fn(() => Promise.resolve([mockDestination])),
}))

// Stub the InteractiveMap to avoid leaflet dependency
const InteractiveMapStub = {
  name: 'InteractiveMap',
  props: ['items', 'center', 'visible', 'title'],
  template: '<div class="interactive-map-stub">map</div>',
}

import DestinationDetailsView from '../src/views/DestinationDetailsView.vue'

describe('DestinationDetailsView', () => {
  it('renders destination details fetched from API/cache', async () => {
    const wrapper = mount(DestinationDetailsView, {
      global: {
        components: { InteractiveMap: InteractiveMapStub },
      },
    })

    // wait for onMounted async
    await new Promise((r) => setTimeout(r, 0))
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Mock Place')
    expect(wrapper.text()).toContain('A lovely mock place')
    // main media shown via img src
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/image.jpg')
    // activities
    expect(wrapper.text()).toContain('Guided tour')
    expect(wrapper.text()).toContain('$10')
    // coordinates
    expect(wrapper.text()).toContain('Lat: 1.23, Lon: 4.56')
  })
})
