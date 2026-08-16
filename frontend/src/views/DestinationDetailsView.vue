<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import backgroundPageDetailAndProfile from '../assets/images/backgrounds/background_page_detail_and_profile.jpg'
import { destinationsCache } from '../stores/destinationsCache'
import { searchDestinations, toggleFavorite } from '../api/destinations'
import InteractiveMap from '../components/InteractiveMap.vue'
import FareCalculator from '../components/FareCalculator.vue'
import AudioPlayButton from '../components/AudioPlayButton.vue'
import CommentSection from '../components/CommentSection.vue'
import { toastStore } from '../stores/toast'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const destination = ref(null)
const allDestinations = ref([])
const loading = ref(true)
const error = ref(null)
const selectedImage = ref(null)
const favoriteBusy = ref(false)
const highlightCommentId = route.query?.comment || null

const mainImage = computed(() => destination.value?.media?.main || null)
const gallery = computed(() => destination.value?.media?.secondary || [])

async function load() {
  loading.value = true
  try {
    const all = await searchDestinations()
    allDestinations.value = all
    destinationsCache.cache(all)
    const d = all.find((item) => item.id === id)
    if (!d) throw new Error('Destination not found')
    destination.value = d
  } catch (e) {
    const cached = destinationsCache.get(id)
    if (cached) {
      destination.value = cached
    } else {
      error.value = e.message || String(e)
    }
  } finally {
    loading.value = false
  }
}

function openImage(image) {
  selectedImage.value = image
}

function closeImage() {
  selectedImage.value = null
}

function planTrip() {
  router.push({ name: 'itineraries', query: { destination_id: destination.value.id } })
}

async function toggleFav() {
  if (!destination.value || favoriteBusy.value) return
  favoriteBusy.value = true
  try {
    const updated = await toggleFavorite(destination.value.id)
    destination.value.is_favorite = updated.is_favorite
    toastStore.info(updated.is_favorite ? 'Ajouté à vos favoris.' : 'Retiré de vos favoris.')
  } catch {
    // interceptor already surfaced a toast
  } finally {
    favoriteBusy.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-10"
      :style="{ backgroundImage: `url(${backgroundPageDetailAndProfile})` }"
    />
    <div class="relative mx-auto max-w-5xl px-6 py-12 sm:px-8">
      <div
        v-if="selectedImage"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-4 py-6"
        @click="closeImage"
      >
        <div class="relative max-h-full max-w-5xl" @click.stop>
          <button
            type="button"
            class="absolute right-3 top-3 rounded-full bg-white/90 px-3 py-2 text-sm font-semibold text-deep-blue shadow-lg"
            @click="closeImage"
          >
            ✕ Fermer
          </button>
          <img :src="selectedImage" alt="Photo agrandie" class="max-h-[80vh] w-full rounded-2xl object-contain shadow-2xl" />
        </div>
      </div>

      <div v-if="loading" class="rounded-2xl bg-white p-8 shadow">Chargement…</div>
      <div v-else-if="error" class="rounded-2xl bg-white p-8 shadow">{{ error }}</div>
      <div v-else class="rounded-3xl bg-white p-6 shadow-lg sm:p-8">
        <button
          type="button"
          class="mb-6 inline-flex items-center rounded-full border border-border-light px-4 py-2 text-sm font-medium text-deep-blue transition hover:bg-sage/10"
          @click="router.back()"
        >
          ← Retour
        </button>

        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <span class="stamp inline-block rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-wider">
              {{ destination.category }}
            </span>
            <h1 class="mt-3 font-display text-3xl font-semibold text-deep-blue sm:text-4xl">
              {{ destination.name }}
            </h1>
            <p class="mt-1 font-mono text-xs uppercase tracking-widest text-text-secondary">
              {{ destination.country }}
            </p>
          </div>
          <div class="flex items-center gap-1 rounded-full bg-lavender-light px-3 py-1.5 text-sm font-semibold text-lavender">
            ⭐ {{ destination.rating?.toFixed(1) }}
          </div>
        </div>

        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-full border-2 px-4 py-2 text-sm font-medium transition disabled:opacity-60"
          :class="destination.is_favorite ? 'border-sage bg-sage/10 text-sage' : 'border-border-light bg-white text-text-secondary hover:border-sage hover:text-sage'"
          :disabled="favoriteBusy"
          @click="toggleFav"
        >
          <span>{{ destination.is_favorite ? '♥' : '♡' }}</span>
          {{ destination.is_favorite ? 'Dans vos favoris' : 'Ajouter aux favoris' }}
        </button>

        <div class="bamileke-band mt-5 rounded-full" />

        <p class="mt-5 text-base leading-relaxed text-text-secondary">{{ destination.description }}</p>

        <div class="mt-4">
          <AudioPlayButton :text="destination.description" />
        </div>

        <div v-if="destination.anecdote" class="mt-5 rounded-2xl border border-lavender/30 bg-lavender-light/50 p-5">
          <p class="flex items-center gap-2 text-sm font-semibold text-deep-blue">
            <span>✨</span> Le saviez-vous ?
          </p>
          <p class="mt-2 text-sm leading-relaxed text-text-primary">{{ destination.anecdote }}</p>
        </div>

        <div class="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div class="lg:col-span-2">
            <div v-if="mainImage" class="overflow-hidden rounded-2xl border border-border-light bg-cream shadow-sm">
              <img
                :src="mainImage"
                :alt="destination.name"
                class="h-80 w-full cursor-zoom-in object-cover transition duration-200 hover:scale-[1.01]"
                @click="openImage(mainImage)"
              />
            </div>
            <div v-else class="flex h-64 w-full items-center justify-center rounded-2xl bg-cream-dark text-text-light">
              Aucune photo disponible
            </div>

            <div v-if="gallery.length" class="mt-4 overflow-x-auto pb-2">
              <div class="flex min-w-max gap-2">
                <img
                  v-for="(s, idx) in gallery"
                  :key="idx"
                  :src="s"
                  class="h-24 w-28 flex-none cursor-zoom-in rounded-xl border border-border-light object-cover shadow-sm"
                  @click="openImage(s)"
                />
              </div>
            </div>

            <div class="mt-6 rounded-2xl border border-border-light bg-cream/70 p-5">
              <h2 class="font-display text-lg font-semibold text-deep-blue">Activités & tarifs</h2>
              <div class="mt-3 space-y-2">
                <div
                  v-for="(a, idx) in destination.activities"
                  :key="idx"
                  class="flex items-center justify-between gap-3 rounded-xl border border-border-light bg-white px-4 py-2.5"
                >
                  <span class="text-sm text-text-primary">{{ a.name }}</span>
                  <span class="font-mono text-sm font-semibold text-sage">{{ a.price }}</span>
                </div>
                <p v-if="!destination.activities || !destination.activities.length" class="text-sm text-text-secondary">
                  Visite libre — {{ destination.price_range_xaf || 'entrée gratuite' }}.
                </p>
              </div>
              <div class="perforated mt-4 pt-4 text-sm text-text-secondary">
                Entrée moyenne :
                <span class="font-semibold text-deep-blue">
                  {{ destination.avg_cost_per_day > 0 ? `${destination.avg_cost_per_day.toLocaleString('fr-FR')} FCFA` : 'Gratuit' }}
                </span>
                · Meilleure période : {{ destination.best_season }}
              </div>
              <p class="mt-3 flex items-start gap-1.5 text-xs leading-relaxed text-text-light">
                <span>ℹ️</span>
                <span>{{ destination.price_note || "Les prix affichés sont des estimations maximales, à titre indicatif — ils se négocient généralement sur place." }}</span>
              </p>
            </div>

            <button
              type="button"
              class="mt-6 w-full rounded-xl bg-deep-blue py-3 text-sm font-semibold text-white transition hover:bg-sage sm:w-auto sm:px-8"
              @click="planTrip"
            >
              Planifier une visite ici
            </button>
          </div>

          <div class="space-y-6">
            <div v-if="destination.latitude && destination.longitude">
              <h3 class="text-sm font-semibold text-deep-blue">Localisation réelle</h3>
              <p class="mt-1 font-mono text-xs text-text-secondary">
                {{ destination.latitude.toFixed(5) }}, {{ destination.longitude.toFixed(5) }}
              </p>
              <div class="mt-2 overflow-hidden rounded-2xl border border-border-light">
                <InteractiveMap
                  :items="[destination]"
                  :center="[destination.latitude, destination.longitude]"
                  :show-user-location="false"
                  visible
                  compact
                  allow-expand
                  title="Localisation"
                />
              </div>
            </div>

            <FareCalculator :destination="destination" :all-destinations="allDestinations" />
          </div>
        </div>

        <div class="mt-8">
          <CommentSection :destination-id="destination.id" :highlight-id="highlightCommentId" />
        </div>
      </div>
    </div>
  </div>
</template>
