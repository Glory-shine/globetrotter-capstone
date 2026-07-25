import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ItineraryCard from '../src/components/ItineraryCard.vue'

const mockDestination = {
  id: 'dest-001',
  name: 'Bali',
  country: 'Indonesia',
  tags: ['beach'],
  climate: 'tropical',
  avg_cost_per_day: 45,
  description: 'Beaches.',
  best_season: 'April-October',
}

const mockItinerary = {
  id: 'itin-001',
  user_id: 'user-1',
  title: 'Bali honeymoon',
  destination_id: 'dest-001',
  start_date: '2026-09-01',
  end_date: '2026-09-07',
  items: [
    { day: 3, activity: 'Rice terrace hike' },
    { day: 1, activity: 'Arrive, beach sunset' },
  ],
  created_at: '2026-07-01T00:00:00',
}

describe('ItineraryCard', () => {
  it('renders the trip title and resolved destination name from mock JSON', () => {
    const wrapper = mount(ItineraryCard, {
      props: { itinerary: mockItinerary, destination: mockDestination },
    })

    expect(wrapper.text()).toContain('Bali honeymoon')
    expect(wrapper.text()).toContain('Bali, Indonesia')
  })

  it('renders the date range and computed trip length', () => {
    const wrapper = mount(ItineraryCard, {
      props: { itinerary: mockItinerary, destination: mockDestination },
    })

    expect(wrapper.text()).toContain('2026-09-01')
    expect(wrapper.text()).toContain('2026-09-07')
    expect(wrapper.text()).toContain('7 days')
  })

  it('renders day-by-day items sorted by day number', () => {
    const wrapper = mount(ItineraryCard, {
      props: { itinerary: mockItinerary, destination: mockDestination },
    })

    const dayMarkers = wrapper.findAll('span.font-mono')
    const dayOrder = wrapper.text()
    // Day 1 activity should appear before Day 3 activity despite input order.
    expect(dayOrder.indexOf('Arrive, beach sunset')).toBeLessThan(
      dayOrder.indexOf('Rice terrace hike')
    )
    expect(dayMarkers.length).toBeGreaterThanOrEqual(2)
  })

  it('falls back gracefully when the destination is unresolved', () => {
    const wrapper = mount(ItineraryCard, {
      props: { itinerary: mockItinerary, destination: null },
    })
    expect(wrapper.text()).toContain('Destination unavailable')
  })

  it('shows an empty state when there are no day items', () => {
    const wrapper = mount(ItineraryCard, {
      props: { itinerary: { ...mockItinerary, items: [] }, destination: mockDestination },
    })
    expect(wrapper.text()).toContain('No day-by-day plan added yet.')
  })
})
