import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LoginForm from '../src/components/LoginForm.vue'

describe('LoginForm', () => {
  it('captures username and password input', async () => {
    const wrapper = mount(LoginForm)

    await wrapper.find('#login-username').setValue('jane_wanders')
    await wrapper.find('#login-password').setValue('supersecret123')

    expect(wrapper.find('#login-username').element.value).toBe('jane_wanders')
    expect(wrapper.find('#login-password').element.value).toBe('supersecret123')
  })

  it('blocks submit and shows an error when the password is too short', async () => {
    const wrapper = mount(LoginForm)

    await wrapper.find('#login-username').setValue('jane_wanders')
    await wrapper.find('#login-password').setValue('short')
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.emitted('submit')).toBeUndefined()
    expect(wrapper.text()).toContain('Password must be at least 8 characters.')
  })

  it('blocks submit when the username is too short', async () => {
    const wrapper = mount(LoginForm)

    await wrapper.find('#login-username').setValue('jo')
    await wrapper.find('#login-password').setValue('supersecret123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.emitted('submit')).toBeUndefined()
    expect(wrapper.text()).toContain('Username must be at least 3 characters.')
  })

  it('emits submit with trimmed credentials when the form is valid', async () => {
    const wrapper = mount(LoginForm)

    await wrapper.find('#login-username').setValue('  jane_wanders  ')
    await wrapper.find('#login-password').setValue('supersecret123')
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.emitted('submit')).toHaveLength(1)
    expect(wrapper.emitted('submit')[0][0]).toEqual({
      username: 'jane_wanders',
      password: 'supersecret123',
    })
  })

  it('disables the submit button while loading', () => {
    const wrapper = mount(LoginForm, { props: { loading: true } })
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('Signing in…')
  })
})
