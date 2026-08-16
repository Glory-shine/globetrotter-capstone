<script setup>
import { useRouter } from 'vue-router'
import { settingsStore } from '../stores/settings'
import { t } from '../i18n'
import backgroundPageDetailAndProfile from '../assets/images/backgrounds/background_page_detail_and_profile.jpg'

const router = useRouter()
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundPageDetailAndProfile})` }"
    />
    <div class="relative mx-auto max-w-2xl px-6 py-12 sm:px-8">
      <div class="rounded-3xl border border-border-light bg-white/85 p-8 shadow-lg backdrop-blur-xl sm:p-10">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="font-display text-3xl font-semibold text-deep-blue">⚙️ {{ t('settings_title') }}</h1>
            <p class="mt-1 text-sm text-text-secondary">{{ t('settings_subtitle') }}</p>
          </div>
          <router-link :to="{ name: 'profile' }" class="text-sm text-sage hover:underline">
            {{ t('settings_back_to_profile') }}
          </router-link>
        </div>

        <!-- Thème -->
        <div class="mt-8 border-t border-border-light pt-6">
          <p class="text-sm font-semibold text-deep-blue">{{ t('settings_theme') }}</p>
          <div class="mt-3 grid grid-cols-2 gap-3">
            <button
              type="button"
              class="flex items-center gap-3 rounded-2xl border-2 px-4 py-3 text-sm font-medium transition"
              :class="settingsStore.state.theme === 'light' ? 'border-sage bg-sage/10 text-sage' : 'border-border-light bg-white text-text-secondary hover:border-sage'"
              @click="settingsStore.setTheme('light')"
            >
              <span class="text-lg">☀️</span> {{ t('settings_theme_light') }}
            </button>
            <button
              type="button"
              class="flex items-center gap-3 rounded-2xl border-2 px-4 py-3 text-sm font-medium transition"
              :class="settingsStore.state.theme === 'dark' ? 'border-sage bg-sage/10 text-sage' : 'border-border-light bg-white text-text-secondary hover:border-sage'"
              @click="settingsStore.setTheme('dark')"
            >
              <span class="text-lg">🌙</span> {{ t('settings_theme_dark') }}
            </button>
          </div>
        </div>

        <!-- Langue -->
        <div class="mt-8 border-t border-border-light pt-6">
          <p class="text-sm font-semibold text-deep-blue">{{ t('settings_language') }}</p>
          <div class="mt-3 grid grid-cols-2 gap-3">
            <button
              type="button"
              class="flex items-center gap-3 rounded-2xl border-2 px-4 py-3 text-sm font-medium transition"
              :class="settingsStore.state.language === 'fr' ? 'border-sage bg-sage/10 text-sage' : 'border-border-light bg-white text-text-secondary hover:border-sage'"
              @click="settingsStore.setLanguage('fr')"
            >
              🇫🇷 Français
            </button>
            <button
              type="button"
              class="flex items-center gap-3 rounded-2xl border-2 px-4 py-3 text-sm font-medium transition"
              :class="settingsStore.state.language === 'en' ? 'border-sage bg-sage/10 text-sage' : 'border-border-light bg-white text-text-secondary hover:border-sage'"
              @click="settingsStore.setLanguage('en')"
            >
              🇬🇧 English
            </button>
          </div>
          <p class="mt-3 text-xs text-text-secondary">
            {{ settingsStore.state.language === 'en'
              ? 'Applies to the app\u2019s navigation and main screens. Place names and descriptions stay in French.'
              : "S'applique à la navigation et aux écrans principaux. Les noms et descriptions des lieux restent en français." }}
          </p>
        </div>

        <button
          type="button"
          class="mt-8 text-sm text-sage hover:underline"
          @click="router.back()"
        >
          ← {{ t('profile_back') }}
        </button>
      </div>
    </div>
  </div>
</template>
