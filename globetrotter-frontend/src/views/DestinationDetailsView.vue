<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import backgroundPageDetailAndProfile from '../assets/images/backgrounds/background_page_detail_and_profile.jpg'
import { destinationsCache } from '../stores/destinationsCache'
import { searchDestinations } from '../api/destinations'
import InteractiveMap from '../components/InteractiveMap.vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const destination = ref(null)
const loading = ref(true)
const error = ref(null)

async function load() {
  loading.value = true
  try {
    let d = destinationsCache.get(id)
    if (!d) {
      const all = await searchDestinations()
      destinationsCache.cache(all)
      d = destinationsCache.get(id)
    }
    if (!d) throw new Error('Destination not found')
    destination.value = d
  } catch (e) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundPageDetailAndProfile})` }"
    />
    <div class="relative mx-auto max-w-4xl px-6 py-12 sm:px-8">
      <div v-if="loading" class="p-8 bg-white rounded-2xl shadow">Loading…</div>
      <div v-else-if="error" class="p-8 bg-white rounded-2xl shadow">{{ error }}</div>
      <div v-else class="bg-white rounded-2xl p-8 shadow">
        <button
          type="button"
          class="mb-6 inline-flex items-center rounded-full border border-border-light px-4 py-2 text-sm font-medium text-deep-blue transition hover:bg-sage/10"
          @click="router.back()"
        >
          ← Back
        </button>
        <h1 class="text-3xl font-display font-semibold text-deep-blue">{{ destination.name }}, {{ destination.country }}</h1>
        <p class="mt-2 text-sm text-text-secondary">{{ destination.description }}</p>

        <div class="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div class="md:col-span-2">
            <div v-if="destination.media && destination.media.main">
              <img v-if="!destination.media.main.endsWith('.mp4')" :src="destination.media.main" alt="main media" class="w-full rounded-lg object-cover" />
              <video v-else controls class="w-full rounded-lg">
                <source :src="destination.media.main" type="video/mp4" />
              </video>
            </div>
            <div v-else class="w-full h-64 rounded-lg bg-paper-dim flex items-center justify-center text-slate">No media available</div>

            <div v-if="destination.media && destination.media.secondary && destination.media.secondary.length" class="mt-4 grid grid-cols-3 gap-2">
              <img v-for="(s, idx) in destination.media.secondary" :key="idx" :src="s" class="w-full h-20 object-cover rounded" />
            </div>

            <div class="mt-6 rounded-2xl border border-border-light bg-cream/70 p-4">
              <h2 class="text-lg font-semibold text-deep-blue">Prices & Activities</h2>
              <div class="mt-3 space-y-3 text-sm text-text-secondary">
                <div v-if="destination.activities && destination.activities.length">
                  <div
                    v-for="(a, idx) in destination.activities"
                    :key="idx"
                    class="flex items-start justify-between gap-3 rounded-xl border border-border-light bg-white/80 px-3 py-2"
                  >
                    <span>{{ a.name }}</span>
                    <span v-if="a.price" class="font-semibold text-sage">{{ a.price }}</span>
                    <span v-else class="text-text-light">Price not listed</span>
                  </div>
                </div>
                <div v-else>No activities data available.</div>
              </div>
            </div>
          </div>

          <div>
            <div>
              <h3 class="text-sm font-semibold">Location</h3>
              <div class="mt-2">
                <p v-if="destination.latitude && destination.longitude" class="text-sm text-text-secondary">Lat: {{ destination.latitude }}, Lon: {{ destination.longitude }}</p>
                <p v-else class="text-sm text-text-secondary">Exact location not available.</p>
              </div>
            </div>

            <div class="mt-4">
              <h3 class="text-sm font-semibold">Map</h3>
              <div class="mt-2">
                <InteractiveMap v-if="destination.latitude && destination.longitude" :items="[destination]" :center="[destination.latitude, destination.longitude]" visible title="Location" />
                <div v-else class="h-40 w-full rounded bg-paper-dim flex items-center justify-center text-slate">No map available</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
