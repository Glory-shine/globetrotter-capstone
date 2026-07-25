import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { authStore } from '../src/stores/auth'

import ProfileView from '../src/views/ProfileView.vue'

describe('ProfileView', () => {
  it('renders profile form and saves updates to authStore', async () => {
    const spy = vi.spyOn(authStore, 'setSession').mockImplementation(() => {})

    const wrapper = mount(ProfileView)
    expect(wrapper.text()).toContain('Profile')
    const usernameInput = wrapper.find('input')
    await usernameInput.setValue('newuser')
    const inputs = wrapper.findAll('input')
    const prefsInput = inputs[1]
    await prefsInput.setValue('mountain, culture')

    // Click the Save button (find by text)
    const btns = wrapper.findAll('button')
    const saveBtn = btns.find((b) => b.text() === 'Save')
    expect(saveBtn).toBeTruthy()
    await saveBtn.trigger('click')

    expect(spy).toHaveBeenCalled()
    const args = spy.mock.calls[0][0]
    expect(args.username).toBe('newuser')
    expect(args.preferences).toEqual(['mountain', 'culture'])

    spy.mockRestore()
  })
})
