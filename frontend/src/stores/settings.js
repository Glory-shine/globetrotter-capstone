import { reactive, readonly, watch } from 'vue'

const THEME_KEY = 'globetrotter_theme'
const LANGUAGE_KEY = 'globetrotter_language'

const state = reactive({
  theme: localStorage.getItem(THEME_KEY) || 'light',
  language: localStorage.getItem(LANGUAGE_KEY) || 'fr',
})

function applyTheme(theme) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('theme-dark', theme === 'dark')
}

function setTheme(theme) {
  state.theme = theme === 'dark' ? 'dark' : 'light'
  localStorage.setItem(THEME_KEY, state.theme)
  applyTheme(state.theme)
}

function setLanguage(language) {
  state.language = language === 'en' ? 'en' : 'fr'
  localStorage.setItem(LANGUAGE_KEY, state.language)
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('lang', state.language)
  }
}

// Apply immediately on load (module init), before any component mounts.
applyTheme(state.theme)
if (typeof document !== 'undefined') {
  document.documentElement.setAttribute('lang', state.language)
}

export const settingsStore = {
  state: readonly(state),
  setTheme,
  setLanguage,
}
