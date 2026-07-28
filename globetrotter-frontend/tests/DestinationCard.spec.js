import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DestinationCard from '../src/components/DestinationCard.vue'

const mockDestination = {
  id: 'dest-001',
  name: 'Bali',
  country: 'Indonesia',
  tags: ['beach', 'nature', 'romantic', 'budget'],
  climate: 'tropical',
  avg_cost_per_day: 45,
  description: 'Volcanic beaches, rice terraces, and laid-back surf towns.',
  best_season: 'April-October',
}

describe('DestinationCard', () => {
  it('renders the destination name, country, and description from mock JSON', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })

    expect(wrapper.text()).toContain('Bali')
    expect(wrapper.text()).toContain('Indonesia')
    expect(wrapper.text()).toContain('Volcanic beaches, rice terraces, and laid-back surf towns.')
  })

  it('renders every tag from the mock data', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })

    for (const tag of mockDestination.tags) {
      expect(wrapper.text().toLowerCase()).toContain(tag)
    }
  })

  it('shows the destination summary without a price tag', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    expect(wrapper.text()).toContain('Volcanic beaches, rice terraces, and laid-back surf towns.')
    expect(wrapper.text()).not.toContain('$45')
    expect(wrapper.text()).not.toContain('/day')
  })

  it('renders a destination image when one is provided', () => {
    const wrapper = mount(DestinationCard, {
      props: {
        destination: {
          ...mockDestination,
          media: {
            main: '/images/destinations/yaounde-food-trail.svg',
          },
        },
      },
    })

    const image = wrapper.find('img[alt="destination image"]')
    expect(image.exists()).toBe(true)
    expect(image.attributes('src')).toContain('/images/destinations/yaounde-food-trail.svg')
  })

  it('shows a match stamp only when matchTags overlap the destination tags', () => {
    const noMatch = mount(DestinationCard, { props: { destination: mockDestination } })
    expect(noMatch.text()).not.toContain('Match')

    const withMatch = mount(DestinationCard, {
      props: { destination: mockDestination, matchTags: ['beach'] },
    })
    expect(withMatch.text()).toContain('Match')
  })

  it('emits "plan" with the destination when the CTA is clicked', async () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    const planButton = wrapper.findAll('button').find((button) => button.text() === 'Plan a trip')

    expect(planButton).toBeTruthy()
    await planButton.trigger('click')

    expect(wrapper.emitted('plan')).toHaveLength(1)
    expect(wrapper.emitted('plan')[0][0]).toEqual(mockDestination)
  })

  it('shows a Details button on the card', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    const buttons = wrapper.findAll('button')
    // There should be at least two buttons: Plan and Details
    expect(buttons.length).toBeGreaterThanOrEqual(2)
    expect(wrapper.text()).toContain('Details')
  })

  it('toggles the like button and updates the likes count', async () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })

    expect(wrapper.text()).toContain('0')
    await wrapper.find('button[aria-label="Like destination"]').trigger('click')

    expect(wrapper.text()).toContain('1')
  })
})
