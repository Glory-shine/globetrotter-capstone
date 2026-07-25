<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import DestinationCard from '../components/DestinationCard.vue'
import InteractiveMap from '../components/InteractiveMap.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { searchDestinations } from '../api/destinations'
import { destinationsCache } from '../stores/destinationsCache'
import { PREFERENCE_TAGS } from '../config'

const router = useRouter()

const filters = reactive({ q: '', tag: '', max_cost: '' })
const results = ref([])
const loading = ref(true)
const showMap = ref(false)
const categoryPills = [
  { key: 'all', label: 'All Destinations', icon: '🗺️' },
  { key: 'food', label: 'Restaurants', icon: '🍽️' },
  { key: 'culture', label: 'Museums', icon: '🏛️' },
  { key: 'nature', label: 'Parks', icon: '🌳' },
  { key: 'nightlife', label: 'Nightlife', icon: '🌙' },
]
const activeCategory = ref('all')
let debounceHandle = null

const visibleResults = computed(() => {
  if (activeCategory.value === 'all') return results.value
  return results.value.filter((item) => {
    const category = (item.category || '').toLowerCase()
    const tags = (item.tags || []).map((tag) => String(tag).toLowerCase())
    if (activeCategory.value === 'food') return category === 'food' || tags.some((tag) => ['food', 'restaurant', 'market', 'boukarou'].includes(tag))
    if (activeCategory.value === 'culture') return category === 'culture' || tags.some((tag) => ['culture', 'history', 'museum', 'chiefdom', 'chefferie'].includes(tag))
    if (activeCategory.value === 'nature') return category === 'nature' || tags.some((tag) => ['nature', 'adventure', 'park', 'waterfall', 'beach', 'ecotourism'].includes(tag))
    if (activeCategory.value === 'nightlife') return category === 'nightlife' || tags.some((tag) => ['nightlife', 'lounge', 'cabaret'].includes(tag))
    return category === activeCategory.value || tags.includes(activeCategory.value)
  })
})

async function runSearch() {
  loading.value = true
  try {
    const data = await searchDestinations(filters)
    results.value = data
    destinationsCache.cache(data)
  } catch {
    // toast already shown by the API client interceptor
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  clearTimeout(debounceHandle)
  debounceHandle = setTimeout(runSearch, 300)
}

function toggleTag(tag) {
  filters.tag = filters.tag === tag ? '' : tag
  runSearch()
}

function clearFilters() {
  filters.q = ''
  filters.tag = ''
  filters.max_cost = ''
  runSearch()
}

function planTrip(destination) {
  router.push({ name: 'itineraries', query: { destination_id: destination.id } })
}

function toggleView() {
  showMap.value = !showMap.value
}

function selectCategory(category) {
  activeCategory.value = category
}

onMounted(runSearch)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div class="mx-auto max-w-7xl px-6 py-12 sm:px-8">
    <div class="max-w-2xl">
      <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Discover</p>
      <h1 class="mt-3 font-display text-5xl font-semibold text-deep-blue sm:text-6xl">
        Where to next?
      </h1>
      <p class="mt-3 text-lg text-text-secondary leading-relaxed">
        Browse curated destinations, filter by what matters, and begin your next adventure.
      </p>
    </div>

    <!-- Search + filters panel -->
    <div class="mt-12 rounded-3xl border border-border-light bg-white/70 backdrop-blur-xl p-8 shadow-lg sm:p-10">
      <div class="flex flex-col gap-4 sm:flex-row">
        <div class="relative flex-1">
          <svg
            class="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-text-light"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
            <path d="m20 20-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
          <input
            v-model="filters.q"
            type="text"
            placeholder="Search by destination, experience, or vibe…"
            class="w-full rounded-2xl border border-border-light bg-cream py-3 pl-12 pr-4 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
            @input="debouncedSearch"
          />
        </div>
        <input
          v-model="filters.max_cost"
          type="number"
          min="0"
          placeholder="Daily budget"
          class="w-full rounded-2xl border border-border-light bg-cream px-4 py-3 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20 sm:w-44"
          @input="debouncedSearch"
        />
      </div>

      <div class="mt-5 flex flex-wrap items-center gap-2">
        <button
          v-for="tag in PREFERENCE_TAGS"
          :key="tag"
          type="button"
          class="rounded-full px-4 py-2 text-xs font-medium capitalize transition duration-200"
          :class="
            filters.tag === tag
              ? 'bg-sage text-white shadow-md'
              : 'bg-lavender-light text-text-primary hover:bg-sage hover:text-white'
          "
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
        <button
          v-if="filters.q || filters.tag || filters.max_cost"
          type="button"
          class="ml-3 text-xs font-medium text-sage underline-offset-2 hover:underline"
          @click="clearFilters"
        >
          Clear all
        </button>
      </div>

      <!-- Category pills -->
      <div class="mt-5 flex flex-wrap items-center gap-3">
        <button
          v-for="pill in categoryPills"
          :key="pill.key"
          type="button"
          class="rounded-full border-2 px-4 py-2 text-xs font-medium transition duration-200"
          :class="
            activeCategory === pill.key
              ? 'border-sage bg-sage/10 text-sage'
              : 'border-border-light bg-white text-text-secondary hover:border-sage hover:text-sage'
          "
          @click="selectCategory(pill.key)"
        >
          <span class="mr-2">{{ pill.icon }}</span>{{ pill.label }}
        </button>
        <button
          type="button"
          class="ml-auto rounded-full border-2 border-border-light bg-white px-4 py-2 text-xs font-medium text-text-secondary transition duration-200 hover:border-sage hover:text-sage"
          @click="toggleView"
        >
          {{ showMap ? '≡ List' : '⊙ Map' }}
        </button>
      </div>
    </div>

    <!-- Results -->
    <div class="mt-16" v-if="showMap">
      <InteractiveMap
        :items="visibleResults"
        :active-category="activeCategory"
        :visible="showMap"
        title="Explore destinations on the map"
      />
    </div>
    <div v-else class="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2">
      <template v-if="loading">
        <SkeletonCard v-for="n in 6" :key="n" />
      </template>
      <template v-else-if="visibleResults.length">
        <DestinationCard
          v-for="dest in visibleResults"
          :key="dest.id"
          :destination="dest"
          @plan="planTrip"
        />
      </template>
      <div v-else class="col-span-full rounded-3xl border border-dashed border-border py-24 text-center">
        <p class="font-display text-2xl text-text-primary">No destinations match your search.</p>
        <p class="mt-2 text-sm text-text-secondary">Try adjusting your filters or search terms.</p>
      </div>
    </div>
    </div>
  </div>
</template>
