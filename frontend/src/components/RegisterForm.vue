<script setup>
import { reactive, ref } from 'vue'
import { PREFERENCE_TAGS } from '../config'

const props = defineProps({
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])

const form = reactive({ username: '', email: '', password: '', preferences: [] })
const errors = reactive({ username: '', email: '', password: '' })
const attempted = ref(false)

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate() {
  errors.username =
    form.username.trim().length >= 3 && form.username.trim().length <= 30
      ? ''
      : 'Username must be 3–30 characters.'
  errors.email = EMAIL_RE.test(form.email.trim()) ? '' : 'Enter a valid email address.'
  errors.password = form.password.length >= 8 ? '' : 'Password must be at least 8 characters.'
  return !errors.username && !errors.email && !errors.password
}

function toggleTag(tag) {
  const idx = form.preferences.indexOf(tag)
  if (idx === -1) form.preferences.push(tag)
  else form.preferences.splice(idx, 1)
}

function handleSubmit() {
  attempted.value = true
  if (!validate()) return
  emit('submit', {
    username: form.username.trim(),
    email: form.email.trim(),
    password: form.password,
    preferences: form.preferences,
  })
}
</script>

<template>
  <form novalidate class="space-y-5" @submit.prevent="handleSubmit">
    <div>
      <label for="reg-username" class="mb-1.5 block text-sm font-medium text-text-primary">Username</label>
      <input
        id="reg-username"
        v-model="form.username"
        type="text"
        autocomplete="username"
        placeholder="jane_wanders"
        class="w-full rounded-xl border bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:ring-2 focus:ring-sage/40"
        :class="attempted && errors.username ? 'border-lavender' : 'border-border-light focus:border-sage'"
      />
      <p v-if="attempted && errors.username" class="mt-1 text-xs text-lavender">{{ errors.username }}</p>
    </div>

    <div>
      <label for="reg-email" class="mb-1.5 block text-sm font-medium text-text-primary">Email</label>
      <input
        id="reg-email"
        v-model="form.email"
        type="email"
        autocomplete="email"
        placeholder="jane@example.com"
        class="w-full rounded-xl border bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:ring-2 focus:ring-sage/40"
        :class="attempted && errors.email ? 'border-lavender' : 'border-border-light focus:border-sage'"
      />
      <p v-if="attempted && errors.email" class="mt-1 text-xs text-lavender">{{ errors.email }}</p>
    </div>

    <div>
      <label for="reg-password" class="mb-1.5 block text-sm font-medium text-text-primary">Password</label>
      <input
        id="reg-password"
        v-model="form.password"
        type="password"
        autocomplete="new-password"
        placeholder="At least 8 characters"
        class="w-full rounded-xl border bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:ring-2 focus:ring-sage/40"
        :class="attempted && errors.password ? 'border-lavender' : 'border-border-light focus:border-sage'"
      />
      <p v-if="attempted && errors.password" class="mt-1 text-xs text-lavender">{{ errors.password }}</p>
    </div>

    <div>
      <span class="mb-2 block text-sm font-medium text-text-primary">Your interests (optional)</span>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tag in PREFERENCE_TAGS"
          :key="tag"
          type="button"
          class="rounded-full px-4 py-2 text-xs font-medium capitalize transition duration-200"
          :class="
            form.preferences.includes(tag)
              ? 'bg-sage text-white shadow-md'
              : 'bg-lavender-light text-text-primary hover:bg-sage hover:text-white'
          "
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>

    <button
      type="submit"
      :disabled="loading"
      class="flex w-full items-center justify-center gap-2 rounded-xl bg-sage py-3 text-sm font-semibold text-white transition hover:bg-sage/90 disabled:cursor-not-allowed disabled:opacity-60"
    >
      <svg v-if="loading" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" opacity="0.3" />
        <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
      </svg>
      {{ loading ? 'Creating account…' : 'Create account' }}
    </button>
  </form>
</template>
