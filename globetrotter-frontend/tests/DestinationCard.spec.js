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

  it('formats the average cost per day', () => {
    const wrapper = mount(DestinationCard, { props: { destination: mockDestination } })
    expect(wrapper.text()).toContain('$45')
    expect(wrapper.text()).toContain('/day')
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

    await wrapper.find('button').trigger('click')

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
})
