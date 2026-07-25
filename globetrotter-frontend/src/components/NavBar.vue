<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../stores/auth'
import { toastStore } from '../stores/toast'

const router = useRouter()
const menuOpen = ref(false)

const links = [
  { to: '/destinations', label: 'Destinations' },
  { to: '/recommendations', label: 'For You' },
  { to: '/itineraries', label: 'Itineraries' },
]

function logout() {
  authStore.clearSession()
  menuOpen.value = false
  toastStore.info('Signed out. Safe travels until next time.')
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-border-light bg-cream/90 backdrop-blur">
    <div class="mx-auto max-w-7xl px-6 sm:px-8">
      <div class="flex h-16 items-center justify-between">
        <!-- Brand -->
        <router-link
          :to="authStore.isAuthenticated() ? '/destinations' : '/login'"
          class="flex items-center gap-2 font-display text-xl font-semibold tracking-tight text-deep-blue"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" class="text-sage">
            <path
              d="M21 3 3 10.5l6.2 1.9L13 20l3-6.3L21 3Z"
              fill="currentColor"
            />
          </svg>
          GlobeTrotter
        </router-link>

        <!-- Desktop nav -->
        <nav v-if="authStore.isAuthenticated()" class="hidden items-center gap-1 sm:flex">
          <router-link
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="rounded-full px-4 py-2 text-sm font-medium text-text-secondary transition hover:bg-lavender-light hover:text-sage"
            active-class="!bg-sage !text-white"
          >
            {{ link.label }}
          </router-link>
        </nav>

        <div class="hidden items-center gap-3 sm:flex">
          <template v-if="authStore.isAuthenticated()">
            <router-link to="/profile" class="text-sm text-text-secondary hover:text-sage">Profile</router-link>
            <span class="font-mono text-xs text-text-secondary">@{{ authStore.state.username }}</span>
            <button
              type="button"
              class="rounded-full border border-border-light px-4 py-2 text-sm font-medium text-text-primary transition hover:border-sage hover:text-sage"
              @click="logout"
            >
              Sign out
            </button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="rounded-full px-4 py-2 text-sm font-medium text-text-primary hover:text-sage"
              >Sign in</router-link
            >
            <router-link
              to="/register"
              class="rounded-full bg-deep-blue px-4 py-2 text-sm font-medium text-white transition hover:bg-sage"
              >Get started</router-link
            >
          </template>
        </div>

        <!-- Mobile toggle -->
        <button
          type="button"
          class="grid h-9 w-9 place-items-center rounded-full text-text-primary sm:hidden"
          aria-label="Toggle menu"
          @click="menuOpen = !menuOpen"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 7h16M4 12h16M4 17h16"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="menuOpen" class="border-t border-border-light bg-cream sm:hidden">
      <div class="mx-auto flex max-w-7xl flex-col gap-1 px-6 py-3 sm:px-8">
        <template v-if="authStore.isAuthenticated()">
          <router-link
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="rounded-lg px-3 py-2 text-sm font-medium text-text-primary hover:bg-lavender-light"
            @click="menuOpen = false"
          >
            {{ link.label }}
          </router-link>
          <button
            type="button"
            class="mt-1 rounded-lg px-3 py-2 text-left text-sm font-medium text-sage hover:bg-sage/10"
            @click="logout"
          >
            Sign out (@{{ authStore.state.username }})
          </button>
        </template>
        <template v-else>
          <router-link
            to="/login"
            class="rounded-lg px-3 py-2 text-sm font-medium text-text-primary hover:bg-lavender-light"
            @click="menuOpen = false"
            >Sign in</router-link
          >
          <router-link
            to="/register"
            class="rounded-lg px-3 py-2 text-sm font-medium text-sage hover:bg-sage/10"
            @click="menuOpen = false"
            >Get started</router-link
          >
        </template>
      </div>
    </div>
  </header>
</template>
