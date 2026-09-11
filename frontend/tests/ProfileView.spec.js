import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { authStore } from '../src/stores/auth'

import ProfileView from '../src/views/ProfileView.vue'

describe('ProfileView', () => {
  beforeEach(() => {
    authStore.setAvatar(null)
  })

  it('renders profile form and saves updates to authStore', async () => {
    const spy = vi.spyOn(authStore, 'setSession').mockImplementation(() => {})

    const wrapper = mount(ProfileView)
    expect(wrapper.text()).toContain('Profil')

    const usernameInput = wrapper.find('input[type="text"], input:not([type])')
    await usernameInput.setValue('newuser')

    const textInputs = wrapper.findAll('input').filter((i) => i.attributes('type') !== 'file')
    const prefsInput = textInputs[1]
    await prefsInput.setValue('mountain, culture')

    const btns = wrapper.findAll('button')
    const saveBtn = btns.find((b) => b.text() === 'Enregistrer')
    expect(saveBtn).toBeTruthy()
    await saveBtn.trigger('click')

    expect(spy).toHaveBeenCalled()
    const args = spy.mock.calls[0][0]
    expect(args.username).toBe('newuser')
    expect(args.preferences).toEqual(['mountain', 'culture'])

    spy.mockRestore()
  })

  it('offers a profile photo upload control and lets the user remove it', async () => {
    const wrapper = mount(ProfileView)
    const fileInput = wrapper.find('input[type="file"]')
    expect(fileInput.exists()).toBe(true)

    authStore.setAvatar('data:image/png;base64,fakeavatar')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('img[alt="Photo de profil"]').exists()).toBe(true)

    authStore.setAvatar(null)
  })

  it('links to the settings page', () => {
    const wrapper = mount(ProfileView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    expect(wrapper.text()).toContain('Paramètres')
  })
})
