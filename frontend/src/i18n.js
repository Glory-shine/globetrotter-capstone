import { computed } from 'vue'
import { settingsStore } from './stores/settings'

// Traductions du "chrome" applicatif (navigation, boutons communs, pages
// Profil/Paramètres). Le contenu éditorial des lieux (noms, descriptions
// réelles saisies en français dans le catalogue) reste en français quelle
// que soit la langue choisie — traduire dynamiquement des centaines de
// champs de contenu réel sort du périmètre de ce réglage d'interface.
const dictionaries = {
  fr: {
    nav_region: 'La région',
    nav_destinations: 'Lieux',
    nav_map: 'Carte',
    nav_recommendations: 'Pour vous',
    nav_itineraries: 'Itinéraires',
    nav_admin: 'Statistiques',
    nav_profile: 'Profil',
    nav_settings: 'Paramètres',
    nav_logout: 'Déconnexion',
    nav_login: 'Se connecter',
    nav_register: 'Créer un compte',
    profile_title: 'Profil',
    profile_subtitle: 'Vos informations et préférences de voyage.',
    profile_username: "Nom d'utilisateur",
    profile_preferences: 'Centres d\u2019intérêt (séparés par des virgules)',
    profile_photo: 'Photo de profil',
    profile_photo_change: 'Changer la photo',
    profile_photo_remove: 'Retirer',
    profile_save: 'Enregistrer',
    profile_saved: 'Profil mis à jour.',
    profile_back: 'Retour',
    settings_title: 'Paramètres',
    settings_subtitle: "Personnalisez l'apparence et la langue de l'application.",
    settings_theme: 'Thème',
    settings_theme_light: 'Clair',
    settings_theme_dark: 'Sombre',
    settings_language: 'Langue',
    settings_back_to_profile: 'Retour au profil',
  },
  en: {
    nav_region: 'The region',
    nav_destinations: 'Places',
    nav_map: 'Map',
    nav_recommendations: 'For you',
    nav_itineraries: 'Itineraries',
    nav_admin: 'Statistics',
    nav_profile: 'Profile',
    nav_settings: 'Settings',
    nav_logout: 'Log out',
    nav_login: 'Log in',
    nav_register: 'Create account',
    profile_title: 'Profile',
    profile_subtitle: 'Your information and travel preferences.',
    profile_username: 'Username',
    profile_preferences: 'Interests (comma-separated)',
    profile_photo: 'Profile photo',
    profile_photo_change: 'Change photo',
    profile_photo_remove: 'Remove',
    profile_save: 'Save',
    profile_saved: 'Profile updated.',
    profile_back: 'Back',
    settings_title: 'Settings',
    settings_subtitle: 'Customize the app\u2019s appearance and language.',
    settings_theme: 'Theme',
    settings_theme_light: 'Light',
    settings_theme_dark: 'Dark',
    settings_language: 'Language',
    settings_back_to_profile: 'Back to profile',
  },
}

export function t(key) {
  const lang = settingsStore.state.language
  return dictionaries[lang]?.[key] || dictionaries.fr[key] || key
}

// Reactive helper for use directly in <template> without recomputing by hand.
export function useI18n() {
  return { t, locale: computed(() => settingsStore.state.language) }
}
