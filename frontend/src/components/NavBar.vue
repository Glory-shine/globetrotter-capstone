<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import logo1 from '../assets/logo/logo1.svg'
import { authStore } from '../stores/auth'
import { toastStore } from '../stores/toast'
import { t } from '../i18n'

const router = useRouter()
const route = useRoute()
const menuOpen = ref(false)

const isAuthRoute = computed(() => route.name === 'login' || route.name === 'register')

const links = computed(() => {
  const base = [
    { to: '/region', label: t('nav_region') },
    { to: '/destinations', label: t('nav_destinations') },
    { to: '/carte', label: t('nav_map') },
    { to: '/recommendations', label: t('nav_recommendations') },
    { to: '/itineraries', label: t('nav_itineraries') },
  ]
  if (authStore.isAdmin()) {
    base.push({ to: '/admin', label: t('nav_admin') })
  }
  return base
})

const initials = computed(() => (authStore.state.username || '?').slice(0, 2).toUpperCase())

function logout() {
  authStore.clearSession()
  menuOpen.value = false
  toastStore.info('Déconnecté. À bientôt pour une prochaine visite !')
  router.push({ name: 'login' })
}
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b border-border-light backdrop-blur"
    :class="isAuthRoute ? 'border-white/20 bg-white/20' : 'border-white/20 bg-white/20'"
  >
    <div class="mx-auto max-w-7xl px-6 sm:px-8">
      <div class="flex h-16 items-center justify-between">
        <!-- Brand -->
        <router-link
          :to="authStore.isAuthenticated() ? '/destinations' : '/login'"
          class="flex items-center gap-3 font-display text-xl font-semibold tracking-tight text-deep-blue"
        >
          <img :src="logo1" alt="GlobeTrotter logo" class="h-10 w-10 rounded-full object-cover shadow-sm" />
          <span class="text-lg sm:text-xl">GlobeTrotter <span class="text-sage">Bafoussam</span></span>
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
            <router-link
              to="/profile"
              class="flex items-center gap-2 text-sm text-text-secondary hover:text-sage"
              :title="t('nav_profile')"
            >
              <img
                v-if="authStore.state.avatar"
                :src="authStore.state.avatar"
                alt=""
                class="h-7 w-7 rounded-full border border-border-light object-cover"
              />
              <span
                v-else
                class="grid h-7 w-7 place-items-center rounded-full bg-sage text-[10px] font-semibold text-white"
              >
                {{ initials }}
              </span>
              {{ t('nav_profile') }}
            </router-link>
            <router-link to="/settings" class="grid h-8 w-8 place-items-center rounded-full text-text-secondary transition hover:bg-lavender-light hover:text-sage" :title="t('nav_settings')" aria-label="Paramètres">
              ⚙️
            </router-link>
            <span class="font-mono text-xs text-text-secondary">@{{ authStore.state.username }}</span>
            <button
              type="button"
              class="rounded-full border border-border-light px-4 py-2 text-sm font-medium text-text-primary transition hover:border-sage hover:text-sage"
              @click="logout"
            >
              {{ t('nav_logout') }}
            </button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="rounded-full px-4 py-2 text-sm font-medium text-text-primary hover:text-sage"
              >{{ t('nav_login') }}</router-link
            >
            <router-link
              to="/register"
              class="rounded-full bg-deep-blue px-4 py-2 text-sm font-medium text-white transition hover:bg-sage"
              >{{ t('nav_register') }}</router-link
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
          <router-link
            to="/profile"
            class="rounded-lg px-3 py-2 text-sm font-medium text-text-primary hover:bg-lavender-light"
            @click="menuOpen = false"
          >
            {{ t('nav_profile') }}
          </router-link>
          <router-link
            to="/settings"
            class="rounded-lg px-3 py-2 text-sm font-medium text-text-primary hover:bg-lavender-light"
            @click="menuOpen = false"
          >
            ⚙️ {{ t('nav_settings') }}
          </router-link>
          <button
            type="button"
            class="mt-1 rounded-lg px-3 py-2 text-left text-sm font-medium text-sage hover:bg-sage/10"
            @click="logout"
          >
            {{ t('nav_logout') }} (@{{ authStore.state.username }})
          </button>
        </template>
        <template v-else>
          <router-link
            to="/login"
            class="rounded-lg px-3 py-2 text-sm font-medium text-text-primary hover:bg-lavender-light"
            @click="menuOpen = false"
            >{{ t('nav_login') }}</router-link
          >
          <router-link
            to="/register"
            class="rounded-lg px-3 py-2 text-sm font-medium text-sage hover:bg-sage/10"
            @click="menuOpen = false"
            >{{ t('nav_register') }}</router-link
          >
        </template>
      </div>
    </div>
  </header>
</template>
