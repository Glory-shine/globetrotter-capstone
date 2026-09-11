import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { settingsStore } from '../src/stores/settings'

import SettingsView from '../src/views/SettingsView.vue'

describe('SettingsView', () => {
  beforeEach(() => {
    settingsStore.setTheme('light')
    settingsStore.setLanguage('fr')
  })

  it('renders theme and language controls', () => {
    const wrapper = mount(SettingsView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    expect(wrapper.text()).toContain('Thème')
    expect(wrapper.text()).toContain('Langue')
    expect(wrapper.text()).toContain('Français')
    expect(wrapper.text()).toContain('English')
  })

  it('switches theme when clicking the dark option', async () => {
    const wrapper = mount(SettingsView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    const darkBtn = wrapper.findAll('button').find((b) => b.text().includes('Sombre'))
    await darkBtn.trigger('click')
    expect(settingsStore.state.theme).toBe('dark')
    settingsStore.setTheme('light')
  })

  it('switches language when clicking English', async () => {
    const wrapper = mount(SettingsView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    const enBtn = wrapper.findAll('button').find((b) => b.text().includes('English'))
    await enBtn.trigger('click')
    expect(settingsStore.state.language).toBe('en')
    settingsStore.setLanguage('fr')
  })
})
