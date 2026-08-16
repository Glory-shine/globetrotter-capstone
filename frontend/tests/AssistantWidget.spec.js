import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

const cheapDestination = {
  id: 'dest-005',
  name: 'Marché A (Grand Marché de Bafoussam)',
  category: 'Marché',
  tags: ['marche', 'gratuit'],
  avg_cost_per_day: 0,
  media: { main: '' },
}
const midDestination = {
  id: 'dest-001',
  name: 'Chefferie Supérieure de Bafoussam',
  category: 'Chefferie',
  tags: ['chefferie', 'culture'],
  avg_cost_per_day: 2000,
  media: { main: '' },
}

const searchDestinations = vi.fn(() => Promise.resolve([cheapDestination, midDestination]))

vi.mock('../src/api/destinations', () => ({
  searchDestinations: (...args) => searchDestinations(...args),
}))

import AssistantWidget from '../src/components/AssistantWidget.vue'

describe('AssistantWidget', () => {
  beforeEach(() => {
    searchDestinations.mockClear()
  })

  it('greets the user before any search', () => {
    const wrapper = mount(AssistantWidget)
    expect(wrapper.text()).toContain('Dites-moi votre budget')
  })

  it('searches with the given budget and shows matching suggestions', async () => {
    const wrapper = mount(AssistantWidget)

    await wrapper.find('#assistant-budget').setValue('1000')
    const askButton = wrapper.findAll('button').find((b) => b.text().includes('Trouver des lieux'))
    await askButton.trigger('click')
    await flushPromises()

    expect(searchDestinations).toHaveBeenCalledWith({ max_cost: 1000, tag: undefined })
    expect(wrapper.text()).toContain('Marché A (Grand Marché de Bafoussam)')
    expect(wrapper.text()).toContain('Chefferie Supérieure de Bafoussam')
  })

  it('includes the selected interest tag in the search', async () => {
    const wrapper = mount(AssistantWidget)

    const chefferieChip = wrapper.findAll('button').find((b) => b.text() === 'chefferie')
    await chefferieChip.trigger('click')

    const askButton = wrapper.findAll('button').find((b) => b.text().includes('Trouver des lieux'))
    await askButton.trigger('click')
    await flushPromises()

    expect(searchDestinations).toHaveBeenCalledWith({ max_cost: undefined, tag: 'chefferie' })
  })

  it('resets the conversation when "Recommencer" is clicked', async () => {
    const wrapper = mount(AssistantWidget)
    const askButton = wrapper.findAll('button').find((b) => b.text().includes('Trouver des lieux'))
    await askButton.trigger('click')
    await flushPromises()

    const resetButton = wrapper.findAll('button').find((b) => b.text() === 'Recommencer')
    expect(resetButton).toBeTruthy()
    await resetButton.trigger('click')

    expect(wrapper.text()).toContain('Dites-moi votre budget')
  })
})
