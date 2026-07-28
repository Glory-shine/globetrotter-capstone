<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import backgroundDestination from '../assets/images/backgrounds/background_destination.jpg'
import DestinationCard from '../components/DestinationCard.vue'
import InteractiveMap from '../components/InteractiveMap.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { searchDestinations } from '../api/destinations'
import { destinationsCache } from '../stores/destinationsCache'
import { PREFERENCE_TAGS } from '../config'

const route = useRoute()
const router = useRouter()

const filters = reactive({ q: '', tag: '', max_cost: '' })
const allDestinations = ref([])
const loading = ref(true)
const showMap = ref(false)
const activeCategory = ref('all')
const selectedImage = ref(null)
const categoryPills = [
  { key: 'all', label: 'All Destinations', icon: '🗺️' },
  { key: 'food', label: 'Restaurants', icon: '🍽️' },
  { key: 'culture', label: 'Museums', icon: '🏛️' },
  { key: 'nature', label: 'Parks', icon: '🌳' },
  { key: 'nightlife', label: 'Nightlife', icon: '🌙' },
]

const regions = [
  { slug: 'centre', title: 'Centre', description: 'Yaoundé and the political heart of the country.', image: '/images/cards_regions images/Card_Centre_Cameroun.jpg', keywords: ['yaounde', 'yaoundé', 'mfoundi', 'bastos', 'ngousso', 'essos', 'mvog', 'mvan', 'centre'] },
  { slug: 'littoral', title: 'Littoral', description: 'Douala, Limbe and the lively coast.', image: '/images/cards_regions images/Card_Littoral_Cameroun.jpg', keywords: ['douala', 'limbe', 'littoral'] },
  { slug: 'south', title: 'South', description: 'Coastal escapes and serene beaches.', image: '/images/cards_regions images/Card_Sud_Cameroun.jpg', keywords: ['kribi', 'south', 'coastal'] },
  { slug: 'southwest', title: 'Southwest', description: 'Highland landscapes around Mount Cameroon.', image: '/images/cards_regions images/Card_south_west_Cameroun.jpg', keywords: ['buea', 'southwest', 'mount', 'cameroon'] },
  { slug: 'north', title: 'North', description: 'Savannahs, wildlife and wide-open horizons.', image: '/images/cards_regions images/Card_North_Cameroun.jpg', keywords: ['waza', 'north', 'savanah'] },
  { slug: 'far-north', title: 'Far North', description: 'Remote and authentic landscapes.', image: '/images/cards_regions images/Card_far_north_cameroun.jpg', keywords: ['far north', 'far-north', 'maroua'] },
  { slug: 'west', title: 'West', description: 'Traditional chiefdoms and cool highlands.', image: '/images/cards_regions images/Card_ouest_cameroun.jpg', keywords: ['bafoussam', 'west', 'chiefdom', 'highland'] },
  { slug: 'northwest', title: 'Northwest', description: 'Village trails and elevated scenery.', image: '/images/cards_regions images/Card_North_West_Cameroun.jpg', keywords: ['bamenda', 'northwest', 'highlands'] },
  { slug: 'east', title: 'East', description: 'Forest-rich landscapes and hidden routes.', image: '/images/cards_regions images/Card_Sud_Cameroun1.jpg', keywords: ['east', 'forest', 'bertoua'] },
  { slug: 'adamawa', title: 'Adamawa', description: 'Plateaus and cultural routes in the interior.', image: '/images/cards_regions images/Card_adamawa_cameroun.jpg', keywords: ['adamawa', 'adamaoua', 'ngaoundere'] },
]

const region = computed(() => regions.find((item) => item.slug === route.params.regionSlug) || regions[0])

function matchesRegion(destination) {
  const text = `${destination.name || ''} ${destination.description || ''} ${(destination.tags || []).join(' ')}`.toLowerCase()
  return (region.value?.keywords || []).some((keyword) => text.includes(keyword.toLowerCase()))
}

const regionDestinations = computed(() => {
  return (allDestinations.value || []).filter(matchesRegion)
})

const visibleResults = computed(() => {
  const query = filters.q.trim().toLowerCase()
  const maxCost = filters.max_cost === '' ? null : Number(filters.max_cost)
  const category = activeCategory.value
  let list = regionDestinations.value

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

  if (category === 'all') return list
  return list.filter((item) => {
    const itemCategory = (item.category || '').toLowerCase()
    const tags = (item.tags || []).map((tag) => String(tag).toLowerCase())
    if (category === 'food') return itemCategory === 'food' || tags.some((tag) => ['food', 'restaurant', 'market', 'boukarou'].includes(tag))
    if (category === 'culture') return itemCategory === 'culture' || tags.some((tag) => ['culture', 'history', 'museum', 'chiefdom', 'chefferie'].includes(tag))
    if (category === 'nature') return itemCategory === 'nature' || tags.some((tag) => ['nature', 'adventure', 'park', 'waterfall', 'beach', 'ecotourism'].includes(tag))
    if (category === 'nightlife') return itemCategory === 'nightlife' || tags.some((tag) => ['nightlife', 'lounge', 'cabaret'].includes(tag))
    return itemCategory === category || tags.includes(category)
  })
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
}

function toggleView() {
  showMap.value = !showMap.value
}

function selectCategory(category) {
  activeCategory.value = category
}

function openImage(image) {
  selectedImage.value = image
}

function closeImage() {
  selectedImage.value = null
}

function planTrip(destination) {
  router.push({ name: 'itineraries', query: { destination_id: destination.id } })
}

watch(
  () => route.params.regionSlug,
  () => {
    clearFilters()
    activeCategory.value = 'all'
    showMap.value = false
    loadDestinations()
  },
  { immediate: true },
)

onMounted(loadDestinations)
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundDestination})` }"
    />
    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
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
            ✕ Close
          </button>
          <img :src="selectedImage" alt="Expanded region image" class="max-h-[80vh] w-full rounded-2xl object-contain shadow-2xl" />
        </div>
      </div>
      <button
        type="button"
        class="mb-6 inline-flex items-center rounded-full border border-border-light bg-white/80 px-4 py-2 text-sm font-medium text-deep-blue transition hover:bg-sage/10"
        @click="router.push({ name: 'destinations' })"
      >
        ← Back to all destinations
      </button>

      <div class="rounded-3xl border border-border-light bg-white/80 p-8 shadow-lg backdrop-blur-xl sm:p-10">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Region explorer</p>
            <h1 class="mt-3 font-display text-4xl font-semibold text-deep-blue sm:text-5xl">
              {{ region?.title }} region
            </h1>
            <p class="mt-3 max-w-2xl text-lg leading-relaxed text-text-secondary">
              {{ region?.description }} Discover the places and destinations that belong to this part of Cameroon.
            </p>
          </div>
          <div class="overflow-hidden rounded-2xl border border-border-light bg-cream shadow-sm">
            <img
              :src="region?.image"
              :alt="region?.title"
              class="h-48 w-full min-w-[18rem] cursor-zoom-in object-cover sm:h-56 lg:h-64 lg:w-80"
              @click="openImage(region?.image)"
            />
          </div>
        </div>

        <div class="mt-8 rounded-3xl border border-border-light bg-cream/70 p-5 sm:p-6">
          <div class="flex flex-col gap-4 sm:flex-row">
            <div class="relative flex-1">
              <svg class="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-text-light" viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
                <path d="m20 20-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
              <input
                v-model="filters.q"
                type="text"
                placeholder="Search within this region…"
                class="w-full rounded-2xl border border-border-light bg-white py-3 pl-12 pr-4 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
              />
            </div>
            <input
              v-model="filters.max_cost"
              type="number"
              min="0"
              placeholder="Daily budget"
              class="w-full rounded-2xl border border-border-light bg-white px-4 py-3 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20 sm:w-44"
            />
          </div>

          <div class="mt-5 flex flex-wrap items-center gap-2">
            <button
              v-for="tag in PREFERENCE_TAGS"
              :key="tag"
              type="button"
              class="rounded-full px-4 py-2 text-xs font-medium capitalize transition duration-200"
              :class="filters.tag === tag ? 'bg-sage text-white shadow-md' : 'bg-white text-text-primary hover:bg-sage hover:text-white'"
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

          <div class="mt-5 flex flex-wrap items-center gap-3">
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
            <button
              type="button"
              class="ml-auto rounded-full border-2 border-border-light bg-white px-4 py-2 text-xs font-medium text-text-secondary transition duration-200 hover:border-sage hover:text-sage"
              @click="toggleView"
            >
              {{ showMap ? '≡ List' : '⊙ Map' }}
            </button>
          </div>
        </div>
      </div>

      <div class="mt-12" v-if="showMap">
        <InteractiveMap :items="visibleResults" :active-category="activeCategory" :visible="showMap" :title="`${region?.title} destinations`" />
      </div>
      <div v-else class="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2">
        <template v-if="loading">
          <SkeletonCard v-for="n in 6" :key="n" />
        </template>
        <template v-else-if="visibleResults.length">
          <DestinationCard v-for="dest in visibleResults" :key="dest.id" :destination="dest" @plan="planTrip" />
        </template>
        <div v-else class="col-span-full rounded-3xl border border-dashed border-border py-24 text-center">
          <p class="font-display text-2xl text-text-primary">No destinations match this region yet.</p>
          <p class="mt-2 text-sm text-text-secondary">Try another search or filter to explore more in this region.</p>
        </div>
      </div>
    </div>
  </div>
</template>
