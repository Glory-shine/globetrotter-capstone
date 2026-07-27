<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import backgroundLoginRegister from '../assets/images/backgrounds/background_login_register.jpg'
import RegisterForm from '../components/RegisterForm.vue'
import { register } from '../api/auth'
import { authStore } from '../stores/auth'
import { toastStore } from '../stores/toast'

const router = useRouter()
const loading = ref(false)

async function handleSubmit(payload) {
  loading.value = true
  try {
    const { access_token } = await register(payload)
    authStore.setSession({
      token: access_token,
      username: payload.username,
      preferences: payload.preferences,
    })
    toastStore.success(`Account created — welcome aboard, ${payload.username}.`)
    router.push({ name: 'destinations' })
  } catch {
    // interceptor already surfaced a toast
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="relative grid min-h-[calc(100vh-4rem)] overflow-hidden lg:grid-cols-2">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-100"
      :style="{ backgroundImage: `url(${backgroundLoginRegister})` }"
    />
    <div class="relative hidden flex-col justify-between overflow-hidden bg-deep-blue px-12 py-16 text-cream lg:flex">
      <div class="absolute inset-0 flight-path opacity-20" />
      <div class="relative">
        <p class="font-mono text-xs uppercase tracking-[0.4em] text-sage">Get started</p>
        <h1 class="mt-4 max-w-sm font-display text-5xl font-light leading-tight">
          Tell us what you love. We'll find the destinations.
        </h1>
      </div>
      <p class="relative max-w-sm text-sm leading-relaxed text-cream/70">
        Your preferences shape every recommendation you receive. Choose as many or as few interests as you like.
      </p>
    </div>

    <div class="flex items-center justify-center px-6 py-16 bg-gradient-to-br from-cream via-lavender-light to-cream">
      <div class="w-full max-w-sm rounded-[28px] border border-white/70 bg-white/70 p-8 shadow-[0_20px_60px_rgba(15,76,92,0.12)] backdrop-blur-sm">
        <h2 class="font-display text-3xl font-light text-deep-blue">Create your account</h2>
        <p class="mt-2 text-sm text-text-secondary">Just a minute of setup, then explore.</p>

        <div class="mt-8">
          <RegisterForm :loading="loading" @submit="handleSubmit" />
        </div>

        <p class="mt-6 text-center text-sm text-text-secondary">
          Already registered?
          <router-link to="/login" class="font-semibold text-sage hover:text-sage/80 transition"
            >Sign in</router-link
          >
        </p>
      </div>
    </div>
  </div>
</template>
