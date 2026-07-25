<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { destinationsCache } from '../stores/destinationsCache'
import { searchDestinations } from '../api/destinations'
import InteractiveMap from '../components/InteractiveMap.vue'

const route = useRoute()
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
  <div class="min-h-screen bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div class="mx-auto max-w-4xl px-6 py-12 sm:px-8">
      <div v-if="loading" class="p-8 bg-white rounded-2xl shadow">Loading…</div>
      <div v-else-if="error" class="p-8 bg-white rounded-2xl shadow">{{ error }}</div>
      <div v-else class="bg-white rounded-2xl p-8 shadow">
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

            <div class="mt-6">
              <h2 class="text-lg font-semibold">Prices & Activities</h2>
              <div class="mt-2 text-sm text-text-secondary">
                <div v-if="destination.activities && destination.activities.length">
                  <ul class="list-disc pl-5">
                    <li v-for="(a, idx) in destination.activities" :key="idx">{{ a.name }} <span v-if="a.price">— {{ a.price }}</span></li>
                  </ul>
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
