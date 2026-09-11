<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import backgroundForYou from '../assets/images/backgrounds/background_for_you.jpg'
import DestinationCard from '../components/DestinationCard.vue'
import InteractiveMap from '../components/InteractiveMap.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import AssistantWidget from '../components/AssistantWidget.vue'
import { getRecommendations } from '../api/recommendations'
import { destinationsCache } from '../stores/destinationsCache'
import { authStore } from '../stores/auth'

const router = useRouter()
const results = ref([])
const loading = ref(true)
const maxBudget = ref('')
const showMap = ref(false)
const activeCategory = ref('all')
const assistantOpen = ref(false)
const filtersOpen = ref(false)
const categoryPills = [
  { key: 'all', label: 'Toutes les suggestions', icon: '🗺️' },
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

function toggleAssistant() {
  assistantOpen.value = !assistantOpen.value
}

const visibleResults = computed(() => {
  if (activeCategory.value === 'all') return results.value
  return results.value.filter((item) => item.category === activeCategory.value)
})

const activeFilterCount = computed(() => {
  let count = 0
  if (maxBudget.value) count += 1
  if (activeCategory.value !== 'all') count += 1
  return count
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
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundForYou})` }"
    />
    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.4em] text-sage">Pour vous</p>
        <h1 class="mt-3 font-display text-6xl font-light text-deep-blue sm:text-7xl">
          Des lieux selon vos goûts
        </h1>
        <p class="mt-4 text-lg text-text-secondary leading-relaxed">
          Basé sur
          <span v-if="authStore.state.preferences.length">
            votre intérêt pour
            <span class="font-semibold text-deep-blue">{{ authStore.state.preferences.join(', ') }}</span>
          </span>
          <span v-else>vos préférences enregistrées</span>
          et les visites que vous avez déjà planifiées à Bafoussam.
        </p>
      </div>

      <!-- Assistant IA : replié derrière une petite icône, pour ne pas encombrer la page -->
      <div class="mt-10">
        <button
          type="button"
          class="inline-flex items-center gap-2.5 rounded-full border border-border-light bg-white/80 py-2.5 pl-2.5 pr-5 text-sm font-semibold text-deep-blue shadow-sm backdrop-blur transition hover:border-sage hover:text-sage"
          :aria-expanded="assistantOpen"
          @click="toggleAssistant"
        >
          <span class="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-sage text-base text-white">🤖</span>
          Assistant IA
          <svg
            class="h-4 w-4 shrink-0 transition-transform"
            :class="{ 'rotate-180': assistantOpen }"
            viewBox="0 0 24 24"
            fill="none"
          >
            <path d="m6 9 6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>

        <div v-if="assistantOpen" class="mt-4">
          <AssistantWidget />
        </div>
      </div>

      <div class="mt-10 rounded-3xl border border-border-light bg-white/70 backdrop-blur-xl p-6 shadow-lg sm:p-7">
        <div class="flex flex-wrap items-center gap-3">
          <p class="mr-auto text-sm text-text-secondary">
            {{ visibleResults.length }} lieu{{ visibleResults.length > 1 ? 'x' : '' }} suggéré{{ visibleResults.length > 1 ? 's' : '' }}
          </p>
          <button
            type="button"
            class="relative rounded-full border-2 px-4 py-2 text-xs font-medium transition duration-200"
            :class="filtersOpen ? 'border-sage bg-sage text-white' : 'border-border-light bg-white text-text-secondary hover:border-sage hover:text-sage'"
            @click="filtersOpen = !filtersOpen"
          >
            ▤ Filtrer
            <span
              v-if="activeFilterCount"
              class="ml-1.5 inline-grid h-4 w-4 place-items-center rounded-full text-[10px] font-bold"
              :class="filtersOpen ? 'bg-white text-sage' : 'bg-sage text-white'"
            >
              {{ activeFilterCount }}
            </span>
          </button>
          <button
            type="button"
            class="rounded-full border-2 border-border-light bg-white px-4 py-2 text-xs font-medium text-text-secondary transition duration-200 hover:border-sage hover:text-sage"
            @click="toggleView"
          >
            {{ showMap ? '≡ Liste' : '⊙ Carte' }}
          </button>
        </div>

        <div v-if="filtersOpen" class="mt-5 space-y-5 border-t border-border-light pt-5">
          <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-text-light">Budget maximum</p>
            <div class="flex flex-wrap items-center gap-3">
              <input
                id="budget"
                v-model="maxBudget"
                type="number"
                min="0"
                placeholder="Sans limite"
                class="w-40 rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
                @change="load"
              />
              <span class="text-xs text-text-secondary">FCFA / jour</span>
            </div>
          </div>

          <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-text-light">Catégorie</p>
            <div class="flex flex-wrap items-center gap-3">
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
        </div>
      </div>

      <div class="mt-16" v-if="showMap">
        <InteractiveMap :items="visibleResults" :active-category="activeCategory" :visible="showMap" title="Votre sélection personnalisée" />
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
          <p class="font-display text-2xl text-text-primary">Aucun lieu ne correspond à ce budget.</p>
          <p class="mt-2 text-sm text-text-secondary">Essayez d'augmenter le budget ou de le supprimer pour voir plus de lieux.</p>
        </div>
      </div>
    </div>
  </div>
</template>
