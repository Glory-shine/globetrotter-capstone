<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import DestinationCard from '../components/DestinationCard.vue'
import InteractiveMap from '../components/InteractiveMap.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import { getRecommendations } from '../api/recommendations'
import { destinationsCache } from '../stores/destinationsCache'
import { authStore } from '../stores/auth'

const router = useRouter()
const results = ref([])
const loading = ref(true)
const maxBudget = ref('')
const showMap = ref(false)
const activeCategory = ref('all')
const categoryPills = [
  { key: 'all', label: 'All Recommendations', icon: '🗺️' },
  { key: 'food', label: 'Restaurants', icon: '🍽️' },
  { key: 'culture', label: 'Museums', icon: '🏛️' },
  { key: 'nature', label: 'Parks', icon: '🌳' },
  { key: 'nightlife', label: 'Nightlife', icon: '🌙' },
]

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

async function load() {
  loading.value = true
  try {
    const data = await getRecommendations({
      limit: 6,
      max_budget: maxBudget.value || undefined,
    })
    results.value = data
    destinationsCache.cache(data)
  } catch {
    // toast already shown
  } finally {
    loading.value = false
  }
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

onMounted(load)
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div class="mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.4em] text-sage">For You</p>
        <h1 class="mt-3 font-display text-6xl font-light text-deep-blue sm:text-7xl">
          Picks matched to your taste
        </h1>
        <p class="mt-4 text-lg text-text-secondary leading-relaxed">
          Built from
          <span v-if="authStore.state.preferences.length">
            your interest in
            <span class="font-semibold text-deep-blue">{{ authStore.state.preferences.join(', ') }}</span>
          </span>
          <span v-else>your saved preferences</span>
          and the trips you've already planned.
        </p>
      </div>

      <div class="mt-12 rounded-3xl border border-border-light bg-white/70 backdrop-blur-xl p-8 shadow-lg sm:p-10">
        <div class="flex flex-wrap items-center gap-4">
          <label for="budget" class="text-sm font-medium text-text-primary">Budget limit:</label>
          <input
            id="budget"
            v-model="maxBudget"
            type="number"
            min="0"
            placeholder="No limit"
            class="rounded-2xl border border-border-light bg-cream px-4 py-3 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20 w-40"
            @change="load"
          />
          <span class="text-sm text-text-secondary">XAF per day</span>
          <button
            type="button"
            class="ml-auto rounded-full border-2 border-border-light bg-white px-4 py-2 text-xs font-medium text-text-secondary transition duration-200 hover:border-sage hover:text-sage"
            @click="toggleView"
          >
            {{ showMap ? '≡ List' : '⊙ Map' }}
          </button>
        </div>

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
        </div>
      </div>

      <div class="mt-16" v-if="showMap">
        <InteractiveMap :items="visibleResults" :active-category="activeCategory" :visible="showMap" title="Your personalized shortlist" />
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
            :match-tags="authStore.state.preferences"
            @plan="planTrip"
          />
        </template>
        <div v-else class="col-span-full rounded-3xl border border-dashed border-border py-24 text-center">
          <p class="font-display text-2xl text-text-primary">Nothing matches that budget yet.</p>
          <p class="mt-2 text-sm text-text-secondary">Try raising your limit or clearing it to see more picks.</p>
        </div>
      </div>
    </div>
  </div>
</template>
