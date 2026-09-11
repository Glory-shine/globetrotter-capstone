<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import backgroundDestination from '../assets/images/backgrounds/background_destination.jpg'
import DestinationCard from '../components/DestinationCard.vue'
import InteractiveMap from '../components/InteractiveMap.vue'
import RouteFareCalculator from '../components/RouteFareCalculator.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { searchDestinations } from '../api/destinations'
import { destinationsCache } from '../stores/destinationsCache'
import { PREFERENCE_TAGS, BAFOUSSAM_CENTER } from '../config'

const router = useRouter()

const filters = reactive({ q: '', tag: '', max_cost: '' })
const allDestinations = ref([])
const loading = ref(true)
const filtersOpen = ref(false)
const mapOpen = ref(false)
const activeCategory = ref('all')

const categoryPills = [
  { key: 'all', label: 'Tout Bafoussam', icon: '🗺️' },
  { key: 'Chefferie', label: 'Chefferies', icon: '👑' },
  { key: 'Musée', label: 'Musées', icon: '🏛️' },
  { key: 'Marché', label: 'Marchés', icon: '🧺' },
  { key: 'Nature', label: 'Nature', icon: '🌿' },
  { key: 'Culture', label: 'Culture', icon: '🥁' },
  { key: 'Hôtel', label: 'Hôtels', icon: '🏨' },
  { key: 'Restaurant', label: 'Restaurants', icon: '🍽️' },
  { key: 'Institution', label: 'Institutions', icon: '🏢' },
  { key: 'Hôpital', label: 'Santé', icon: '🏥' },
  { key: 'Pharmacie', label: 'Pharmacies', icon: '💊' },
  { key: 'École', label: 'Écoles', icon: '🎒' },
  { key: 'Lycée', label: 'Lycées', icon: '🏫' },
  { key: 'Université', label: 'Universités', icon: '🎓' },
]

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.tag) count += 1
  if (filters.max_cost) count += 1
  if (activeCategory.value !== 'all') count += 1
  return count
})

const visibleResults = computed(() => {
  const query = filters.q.trim().toLowerCase()
  const maxCost = filters.max_cost === '' ? null : Number(filters.max_cost)
  let list = allDestinations.value

  if (query) {
    list = list.filter((item) => {
      const haystack = `${item.name || ''} ${item.description || ''} ${(item.tags || []).join(' ')}`.toLowerCase()
      return haystack.includes(query)
    })
  }

  if (filters.tag) {
    list = list.filter((item) => (item.tags || []).some((tag) => tag.toLowerCase() === filters.tag.toLowerCase()))
  }

  if (maxCost !== null && !Number.isNaN(maxCost)) {
    list = list.filter((item) => Number(item.avg_cost_per_day || 0) <= maxCost)
  }

  if (activeCategory.value !== 'all') {
    list = list.filter((item) => item.category === activeCategory.value)
  }

  return list
})

async function loadDestinations() {
  loading.value = true
  try {
    const data = await searchDestinations({})
    allDestinations.value = data
    destinationsCache.cache(data)
  } catch {
    // toast already shown by the API client interceptor
  } finally {
    loading.value = false
  }
}

function toggleTag(tag) {
  filters.tag = filters.tag === tag ? '' : tag
}

function clearFilters() {
  filters.q = ''
  filters.tag = ''
  filters.max_cost = ''
  activeCategory.value = 'all'
}

function toggleFilters() {
  filtersOpen.value = !filtersOpen.value
}

function toggleMap() {
  mapOpen.value = !mapOpen.value
}

function pickRandomDestination() {
  const pool = allDestinations.value.length ? allDestinations.value : []
  if (!pool.length) return
  const pick = pool[Math.floor(Math.random() * pool.length)]
  router.push({ name: 'destinationDetails', params: { id: pick.id } })
}

function selectCategory(category) {
  activeCategory.value = category
}

function planTrip(destination) {
  router.push({ name: 'itineraries', query: { destination_id: destination.id } })
}

onMounted(loadDestinations)
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-10"
      :style="{ backgroundImage: `url(${backgroundDestination})` }"
    />
    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Bafoussam, Ouest-Cameroun</p>
        <h1 class="mt-3 font-display text-5xl font-semibold text-deep-blue sm:text-6xl">
          Explorez la ville
        </h1>
        <p class="mt-3 text-lg leading-relaxed text-text-secondary">
          Chefferies, musées, marchés, hôtels, restaurants et sites naturels réels — avec coordonnées
          GPS, photos, et le prix des activités quand elles existent.
        </p>
      </div>
      <div class="bamileke-band mt-6 max-w-2xl rounded-full" />

      <!-- Barre de recherche simple + carte et filtres au clic -->
      <div class="mt-10 rounded-3xl border border-border-light bg-white/80 p-5 shadow-lg backdrop-blur-xl sm:p-6">
        <div class="flex flex-col gap-3 sm:flex-row">
          <div class="relative flex-1">
            <svg class="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-text-light" viewBox="0 0 24 24" fill="none">
              <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
              <path d="m20 20-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            <input
              v-model="filters.q"
              type="text"
              placeholder="Rechercher un lieu — « chefferie », « marché », « hôtel »…"
              class="w-full rounded-2xl border border-border-light bg-cream py-3 pl-12 pr-4 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
            />
          </div>
          <button
            type="button"
            class="relative inline-flex items-center justify-center gap-2 rounded-2xl border-2 px-5 py-3 text-sm font-semibold transition"
            :class="mapOpen ? 'border-sage bg-sage text-white' : 'border-border-light bg-white text-deep-blue hover:border-sage hover:text-sage'"
            @click="toggleMap"
          >
            🗺️ Carte
          </button>
          <button
            type="button"
            class="relative inline-flex items-center justify-center gap-2 rounded-2xl border-2 px-5 py-3 text-sm font-semibold transition"
            :class="filtersOpen ? 'border-sage bg-sage text-white' : 'border-border-light bg-white text-deep-blue hover:border-sage hover:text-sage'"
            @click="toggleFilters"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none">
              <path d="M4 6h16M7 12h10M10 18h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
            </svg>
            Filtrer
            <span
              v-if="activeFilterCount"
              class="grid h-5 w-5 place-items-center rounded-full text-[10px] font-bold"
              :class="filtersOpen ? 'bg-white text-sage' : 'bg-sage text-white'"
            >
              {{ activeFilterCount }}
            </span>
          </button>
        </div>

        <!-- Aperçu carte + tarifs, replié par défaut ; la carte complète vit sur sa propre page -->
        <div v-if="mapOpen" class="mt-5 border-t border-border-light pt-5">
          <div class="mb-3 flex items-center justify-between">
            <p class="text-xs text-text-secondary">Aperçu rapide — pour la carte détaillée avec itinéraires, direction la page dédiée.</p>
            <router-link :to="{ name: 'map' }" class="shrink-0 text-xs font-semibold text-sage hover:underline">
              Carte complète →
            </router-link>
          </div>
          <div class="grid grid-cols-1 gap-6 lg:grid-cols-[1.5fr_1fr]">
            <InteractiveMap
              :items="allDestinations"
              active-category="all"
              :visible="mapOpen"
              title="Aperçu de la carte"
              :center="BAFOUSSAM_CENTER"
              compact
            />
            <RouteFareCalculator :destinations="allDestinations" />
          </div>
        </div>

        <!-- Panneau de filtres, organisé par section, visible uniquement au clic -->
        <div v-if="filtersOpen" class="mt-5 space-y-5 border-t border-border-light pt-5">
          <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-text-light">Catégorie</p>
            <div class="flex flex-wrap items-center gap-2">
              <button
                v-for="pill in categoryPills"
                :key="pill.key"
                type="button"
                class="rounded-full border-2 px-4 py-2 text-xs font-medium transition duration-200"
                :class="activeCategory === pill.key ? 'border-sage bg-sage/10 text-sage' : 'border-border-light bg-white text-text-secondary hover:border-sage hover:text-sage'"
                @click="selectCategory(pill.key)"
              >
                <span class="mr-2">{{ pill.icon }}</span>{{ pill.label }}
              </button>
            </div>
          </div>

          <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-text-light">Centres d'intérêt</p>
            <div class="flex flex-wrap items-center gap-2">
              <button
                v-for="tag in PREFERENCE_TAGS"
                :key="tag"
                type="button"
                class="rounded-full px-4 py-2 text-xs font-medium capitalize transition duration-200"
                :class="filters.tag === tag ? 'bg-sage text-white shadow-md' : 'bg-cream text-text-primary hover:bg-sage hover:text-white'"
                @click="toggleTag(tag)"
              >
                {{ tag }}
              </button>
            </div>
          </div>

          <div class="flex flex-wrap items-end gap-4">
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-text-light">Budget maximum</p>
              <input
                v-model="filters.max_cost"
                type="number"
                min="0"
                placeholder="Budget max (FCFA)"
                class="w-48 rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
              />
            </div>

            <button
              type="button"
              class="rounded-full border-2 border-sage/40 bg-sage/5 px-4 py-2.5 text-xs font-medium text-sage transition duration-200 hover:border-sage hover:bg-sage hover:text-white"
              title="Découvrir un lieu au hasard"
              @click="pickRandomDestination"
            >
              🎲 Surprends-moi
            </button>

            <button
              v-if="filters.q || filters.tag || filters.max_cost || activeCategory !== 'all'"
              type="button"
              class="ml-auto text-xs font-medium text-sage underline-offset-2 hover:underline"
              @click="clearFilters"
            >
              Tout effacer
            </button>
          </div>
        </div>
      </div>

      <div class="mt-10 grid grid-cols-1 gap-8 sm:grid-cols-2 xl:grid-cols-3">
        <template v-if="loading">
          <SkeletonCard v-for="n in 6" :key="n" />
        </template>
        <template v-else-if="visibleResults.length">
          <DestinationCard v-for="dest in visibleResults" :key="dest.id" :destination="dest" @plan="planTrip" />
        </template>
        <div v-else class="col-span-full rounded-3xl border border-dashed border-border py-24 text-center">
          <p class="font-display text-2xl text-text-primary">Aucun lieu ne correspond à ces critères.</p>
          <p class="mt-2 text-sm text-text-secondary">Essayez une autre recherche ou effacez les filtres.</p>
        </div>
      </div>
    </div>
  </div>
</template>
