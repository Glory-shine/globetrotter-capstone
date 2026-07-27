<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import backgroundItineraire from '../assets/images/backgrounds/background_itineraire.jpg'
import ItineraryForm from '../components/ItineraryForm.vue'
import ItineraryCard from '../components/ItineraryCard.vue'
import InteractiveMap from '../components/InteractiveMap.vue'
import { searchDestinations } from '../api/destinations'
import { listItineraries } from '../api/itineraries'
import { destinationsCache } from '../stores/destinationsCache'

const route = useRoute()
const destinations = ref([])
const itineraries = ref([])
const loading = ref(true)
const showMap = ref(false)

async function loadAll() {
  loading.value = true
  try {
    const [destData, itinData] = await Promise.all([searchDestinations(), listItineraries()])
    destinations.value = destData
    destinationsCache.cache(destData)
    itineraries.value = itinData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch {
    // toast already shown
  } finally {
    loading.value = false
  }
}

function onCreated(newItinerary) {
  itineraries.value = [newItinerary, ...itineraries.value]
}

function toggleView() {
  showMap.value = !showMap.value
}

onMounted(loadAll)
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundItineraire})` }"
    />
    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.4em] text-sage">Trip Planner</p>
        <h1 class="mt-3 font-display text-6xl font-light text-deep-blue sm:text-7xl">Your itineraries</h1>
        <p class="mt-4 text-lg text-text-secondary leading-relaxed">
          Plan your days, refine your route, and save it for later.
        </p>
      </div>

      <div class="mt-12 flex items-center justify-end">
        <button
          type="button"
          class="rounded-full border-2 border-border-light bg-white px-4 py-2 text-xs font-medium text-text-secondary transition duration-200 hover:border-sage hover:text-sage"
          @click="toggleView"
        >
          {{ showMap ? '≡ List view' : '⊙ Map view' }}
        </button>
      </div>

      <div class="mt-16" v-if="showMap">
        <InteractiveMap :items="destinations" :active-category="'all'" :visible="showMap" title="All destinations on your trips" />
      </div>

      <div class="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-5" v-else>
        <div class="lg:col-span-2">
          <ItineraryForm
            :destinations="destinations"
            :initial-destination-id="route.query.destination_id || ''"
            @created="onCreated"
          />
        </div>

        <div class="space-y-6 lg:col-span-3">
          <template v-if="loading">
            <div v-for="n in 2" :key="n" class="h-40 animate-pulse rounded-2xl bg-lavender-light/50" />
          </template>
          <template v-else-if="itineraries.length">
            <ItineraryCard
              v-for="it in itineraries"
              :key="it.id"
              :itinerary="it"
              :destination="destinationsCache.get(it.destination_id)"
            />
          </template>
          <div v-else class="rounded-3xl border border-dashed border-border py-24 text-center">
            <p class="font-display text-2xl text-text-primary">No itineraries yet.</p>
            <p class="mt-2 text-sm text-text-secondary">Fill out the form on the left to create your first trip.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
