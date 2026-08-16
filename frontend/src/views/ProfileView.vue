<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../stores/auth'
import { t } from '../i18n'
import { listFavorites, toggleFavorite } from '../api/destinations'
import { listMyComments } from '../api/comments'
import { toastStore } from '../stores/toast'
import DestinationCard from '../components/DestinationCard.vue'
import backgroundPageDetailAndProfile from '../assets/images/backgrounds/background_page_detail_and_profile.jpg'

const router = useRouter()
const username = ref(authStore.state.username || '')
const preferencesText = ref((authStore.state.preferences || []).join(', '))
const saving = ref(false)
const message = ref(null)
const avatarInput = ref(null)
const avatarError = ref('')

const activeTab = ref('infos')
const favorites = ref([])
const favoritesLoading = ref(false)
const myComments = ref([])
const commentsLoading = ref(false)

const initials = () => (authStore.state.username || '?').slice(0, 2).toUpperCase()

function triggerAvatarPicker() {
  avatarInput.value?.click()
}

function onAvatarSelected(event) {
  avatarError.value = ''
  const file = event.target.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    avatarError.value = 'Veuillez choisir un fichier image.'
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    avatarError.value = 'Image trop lourde (2 Mo maximum).'
    return
  }

  const reader = new FileReader()
  reader.onload = () => authStore.setAvatar(reader.result)
  reader.onerror = () => {
    avatarError.value = "Impossible de lire cette image."
  }
  reader.readAsDataURL(file)
  event.target.value = ''
}

function removeAvatar() {
  authStore.setAvatar(null)
}

function saveProfile() {
  saving.value = true
  try {
    const prefs = preferencesText.value
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    authStore.setSession({ token: authStore.state.token, username: username.value, preferences: prefs })
    message.value = t('profile_saved')
  } catch {
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

async function loadFavorites() {
  favoritesLoading.value = true
  try {
    favorites.value = await listFavorites()
  } catch {
    // interceptor already surfaced a toast
  } finally {
    favoritesLoading.value = false
  }
}

async function loadMyComments() {
  commentsLoading.value = true
  try {
    myComments.value = await listMyComments()
  } catch {
    // interceptor already surfaced a toast
  } finally {
    commentsLoading.value = false
  }
}

async function removeFavorite(destination) {
  try {
    await toggleFavorite(destination.id)
    favorites.value = favorites.value.filter((d) => d.id !== destination.id)
    toastStore.info('Retiré de vos favoris.')
  } catch {
    // interceptor already surfaced a toast
  }
}

function goToComment(comment) {
  router.push({
    name: 'destinationDetails',
    params: { id: comment.destination_id },
    query: { comment: comment.id },
  })
}

function selectTab(tab) {
  activeTab.value = tab
  if (tab === 'favorites' && !favorites.value.length) loadFavorites()
  if (tab === 'comments' && !myComments.value.length) loadMyComments()
}

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return "à l'instant"
  if (minutes < 60) return `il y a ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `il y a ${hours} h`
  const days = Math.floor(hours / 24)
  return `il y a ${days} j`
}

onMounted(() => {
  // Favoris et commentaires sont chargés paresseusement, au premier clic
  // sur leur onglet (voir selectTab), pour ne pas alourdir le chargement
  // initial de la page Profil.
})
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundPageDetailAndProfile})` }"
    />
    <div class="relative mx-auto max-w-4xl px-6 py-12 sm:px-8">
      <div class="rounded-3xl border border-border-light bg-white/85 p-8 shadow-lg backdrop-blur-xl sm:p-10">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="font-display text-3xl font-semibold text-deep-blue">{{ t('profile_title') }}</h1>
            <p class="mt-1 text-sm text-text-secondary">{{ t('profile_subtitle') }}</p>
          </div>
          <div class="flex items-center gap-3">
            <router-link
              :to="{ name: 'settings' }"
              class="inline-flex items-center gap-2 rounded-full border border-border-light bg-white px-4 py-2 text-sm font-medium text-deep-blue transition hover:border-sage hover:text-sage"
            >
              ⚙️ {{ t('nav_settings') }}
            </router-link>
            <button type="button" class="text-sm text-sage hover:underline" @click="goBack">{{ t('profile_back') }}</button>
          </div>
        </div>

        <!-- Photo de profil -->
        <div class="mt-8 flex items-center gap-5">
          <div class="relative">
            <img
              v-if="authStore.state.avatar"
              :src="authStore.state.avatar"
              alt="Photo de profil"
              class="h-20 w-20 rounded-full border-2 border-white object-cover shadow-md"
            />
            <div
              v-else
              class="grid h-20 w-20 place-items-center rounded-full border-2 border-white bg-sage text-xl font-semibold text-white shadow-md"
            >
              {{ initials() }}
            </div>
          </div>
          <div>
            <p class="text-sm font-semibold text-deep-blue">{{ t('profile_photo') }}</p>
            <div class="mt-2 flex items-center gap-3">
              <button
                type="button"
                class="rounded-full border-2 border-border-light bg-white px-4 py-2 text-xs font-medium text-deep-blue transition hover:border-sage hover:text-sage"
                @click="triggerAvatarPicker"
              >
                {{ t('profile_photo_change') }}
              </button>
              <button
                v-if="authStore.state.avatar"
                type="button"
                class="text-xs font-medium text-sage hover:underline"
                @click="removeAvatar"
              >
                {{ t('profile_photo_remove') }}
              </button>
            </div>
            <p v-if="avatarError" class="mt-1.5 text-xs text-sage">{{ avatarError }}</p>
            <input ref="avatarInput" type="file" accept="image/*" class="hidden" @change="onAvatarSelected" />
          </div>
        </div>

        <!-- Onglets : Informations / Favoris / Commentaires -->
        <div class="mt-8 flex gap-2 border-b border-border-light">
          <button
            type="button"
            class="rounded-t-xl px-4 py-2.5 text-sm font-medium transition"
            :class="activeTab === 'infos' ? 'border-b-2 border-sage text-sage' : 'text-text-secondary hover:text-sage'"
            @click="selectTab('infos')"
          >
            Informations
          </button>
          <button
            type="button"
            class="rounded-t-xl px-4 py-2.5 text-sm font-medium transition"
            :class="activeTab === 'favorites' ? 'border-b-2 border-sage text-sage' : 'text-text-secondary hover:text-sage'"
            @click="selectTab('favorites')"
          >
            ♥ Mes favoris
          </button>
          <button
            type="button"
            class="rounded-t-xl px-4 py-2.5 text-sm font-medium transition"
            :class="activeTab === 'comments' ? 'border-b-2 border-sage text-sage' : 'text-text-secondary hover:text-sage'"
            @click="selectTab('comments')"
          >
            💬 Mes commentaires
          </button>
        </div>

        <!-- Onglet Informations -->
        <div v-if="activeTab === 'infos'" class="mt-8 grid gap-5">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">{{ t('profile_username') }}</label>
            <input
              v-model="username"
              class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">{{ t('profile_preferences') }}</label>
            <input
              v-model="preferencesText"
              class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
            />
          </div>

          <div class="flex items-center gap-4">
            <button
              type="button"
              class="rounded-full bg-deep-blue px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-sage disabled:opacity-60"
              :disabled="saving"
              @click="saveProfile"
            >
              {{ t('profile_save') }}
            </button>
            <div v-if="message" class="text-sm text-text-secondary">{{ message }}</div>
          </div>
        </div>

        <!-- Onglet Favoris -->
        <div v-else-if="activeTab === 'favorites'" class="mt-8">
          <div v-if="favoritesLoading" class="animate-pulse text-sm text-text-secondary">Chargement de vos favoris…</div>
          <div v-else-if="!favorites.length" class="rounded-2xl border border-dashed border-border-light py-14 text-center">
            <p class="text-sm text-text-secondary">
              Aucun favori pour l'instant. Cliquez sur ♡ sur un lieu pour l'ajouter ici.
            </p>
          </div>
          <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div v-for="dest in favorites" :key="dest.id" class="relative">
              <DestinationCard :destination="dest" @plan="() => router.push({ name: 'itineraries', query: { destination_id: dest.id } })" />
              <button
                type="button"
                class="absolute right-3 top-3 rounded-full bg-white/90 px-2.5 py-1 text-xs font-medium text-sage shadow hover:bg-white"
                title="Retirer des favoris"
                @click="removeFavorite(dest)"
              >
                Retirer
              </button>
            </div>
          </div>
        </div>

        <!-- Onglet Commentaires -->
        <div v-else-if="activeTab === 'comments'" class="mt-8">
          <div v-if="commentsLoading" class="animate-pulse text-sm text-text-secondary">Chargement de vos commentaires…</div>
          <div v-else-if="!myComments.length" class="rounded-2xl border border-dashed border-border-light py-14 text-center">
            <p class="text-sm text-text-secondary">Vous n'avez pas encore commenté de lieu.</p>
          </div>
          <div v-else class="space-y-3">
            <button
              v-for="comment in myComments"
              :key="comment.id"
              type="button"
              class="block w-full rounded-2xl border border-border-light bg-white p-4 text-left transition hover:border-sage hover:shadow-sm"
              @click="goToComment(comment)"
            >
              <div class="flex items-center justify-between gap-3">
                <span class="text-sm font-semibold text-deep-blue">{{ comment.destination_name }}</span>
                <span class="shrink-0 text-xs text-text-light">{{ timeAgo(comment.created_at) }}</span>
              </div>
              <p class="mt-1.5 text-sm leading-relaxed text-text-secondary">{{ comment.text }}</p>
              <span class="mt-2 inline-block text-xs font-medium text-sage">Retrouver mon commentaire →</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
