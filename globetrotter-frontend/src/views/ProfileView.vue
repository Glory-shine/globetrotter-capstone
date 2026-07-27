<script setup>
import { ref } from 'vue'
import { authStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import backgroundPageDetailAndProfile from '../assets/images/backgrounds/background_page_detail_and_profile.jpg'

const router = useRouter()
const username = ref(authStore.state.username || '')
const preferencesText = ref((authStore.state.preferences || []).join(', '))
const saving = ref(false)
const message = ref(null)

function saveProfile() {
  saving.value = true
  // simple local update via authStore.setSession; keep existing token
  try {
    const prefs = preferencesText.value
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    authStore.setSession({ token: authStore.state.token, username: username.value, preferences: prefs })
    message.value = 'Profile updated.'
  } catch (e) {
    message.value = 'Failed to update profile.'
  } finally {
    saving.value = false
  }
}

function goBack() {
  if (router && typeof router.back === 'function') {
    router.back()
  }
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundPageDetailAndProfile})` }"
    />
    <div class="relative mx-auto max-w-3xl px-6 py-12 sm:px-8">
      <div class="bg-white rounded-2xl p-8 shadow">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-display font-semibold text-deep-blue">Profile</h1>
          <button class="text-sm text-sage" @click="goBack">Back</button>
        </div>

        <div class="mt-6 grid gap-4">
          <label class="text-sm font-medium">Username</label>
          <input v-model="username" class="rounded-lg border px-3 py-2" />

          <label class="text-sm font-medium">Preferences (comma-separated)</label>
          <input v-model="preferencesText" class="rounded-lg border px-3 py-2" />

          <div class="flex items-center gap-3">
            <button class="rounded-xl bg-deep-blue px-4 py-2 text-white" :disabled="saving" @click="saveProfile">Save</button>
            <div v-if="message" class="text-sm text-text-secondary">{{ message }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
