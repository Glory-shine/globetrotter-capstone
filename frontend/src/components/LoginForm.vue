<script setup>
import { reactive, ref } from 'vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])

const form = reactive({ username: '', password: '' })
const errors = reactive({ username: '', password: '' })
const attempted = ref(false)

function validate() {
  errors.username = form.username.trim().length >= 3 ? '' : 'Username must be at least 3 characters.'
  errors.password = form.password.length >= 8 ? '' : 'Password must be at least 8 characters.'
  return !errors.username && !errors.password
}

function handleSubmit() {
  attempted.value = true
  if (!validate()) return
  emit('submit', { username: form.username.trim(), password: form.password })
}
</script>

<template>
  <form novalidate class="space-y-5" @submit.prevent="handleSubmit">
    <div>
      <label for="login-username" class="mb-1.5 block text-sm font-medium text-text-primary">Username</label>
      <input
        id="login-username"
        v-model="form.username"
        type="text"
        autocomplete="username"
        placeholder="jane_wanders"
        class="w-full rounded-xl border bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:ring-2 focus:ring-sage/40"
        :class="attempted && errors.username ? 'border-lavender' : 'border-border-light focus:border-sage'"
        @blur="attempted && validate()"
      />
      <p v-if="attempted && errors.username" class="mt-1 text-xs text-lavender">{{ errors.username }}</p>
    </div>

    <div>
      <label for="login-password" class="mb-1.5 block text-sm font-medium text-text-primary">Password</label>
      <input
        id="login-password"
        v-model="form.password"
        type="password"
        autocomplete="current-password"
        placeholder="••••••••"
        class="w-full rounded-xl border bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:ring-2 focus:ring-sage/40"
        :class="attempted && errors.password ? 'border-lavender' : 'border-border-light focus:border-sage'"
        @blur="attempted && validate()"
      />
      <p v-if="attempted && errors.password" class="mt-1 text-xs text-lavender">{{ errors.password }}</p>
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
      {{ loading ? 'Signing in…' : 'Sign in' }}
    </button>
  </form>
</template>
