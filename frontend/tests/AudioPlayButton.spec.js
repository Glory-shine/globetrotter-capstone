import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AudioPlayButton from '../src/components/AudioPlayButton.vue'

describe('AudioPlayButton', () => {
  beforeEach(() => {
    window.speechSynthesis = {
      speak: vi.fn(),
      cancel: vi.fn(),
    }
    global.SpeechSynthesisUtterance = vi.fn().mockImplementation(function (text) {
      this.text = text
    })
  })

  it('renders the play label when idle', () => {
    const wrapper = mount(AudioPlayButton, { props: { text: 'Une description à lire.' } })
    expect(wrapper.text()).toContain('Écouter la description')
  })

  it('starts speech synthesis with French language on click', async () => {
    const wrapper = mount(AudioPlayButton, { props: { text: 'Une description à lire.' } })
    await wrapper.find('button').trigger('click')

    expect(window.speechSynthesis.speak).toHaveBeenCalledTimes(1)
    const utterance = window.speechSynthesis.speak.mock.calls[0][0]
    expect(utterance.text).toBe('Une description à lire.')
    expect(utterance.lang).toBe('fr-FR')
    expect(wrapper.text()).toContain('Arrêter la lecture')
  })

  it('stops speech synthesis when clicked again while speaking', async () => {
    const wrapper = mount(AudioPlayButton, { props: { text: 'Une description à lire.' } })
    await wrapper.find('button').trigger('click')
    await wrapper.find('button').trigger('click')

    expect(window.speechSynthesis.cancel).toHaveBeenCalled()
    expect(wrapper.text()).toContain('Écouter la description')
  })

  it('uses a custom label when provided', () => {
    const wrapper = mount(AudioPlayButton, { props: { text: 'Texte', label: 'Écouter' } })
    expect(wrapper.text()).toContain('Écouter')
  })
})
