<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import backgroundPageDetailAndProfile from '../assets/images/backgrounds/background_page_detail_and_profile.jpg'
import { destinationsCache } from '../stores/destinationsCache'
import { searchDestinations } from '../api/destinations'
import InteractiveMap from '../components/InteractiveMap.vue'

const imageByName = {
  'Yaoundé Food Trail': '/images/destinations/real/yaounde-food-trail.jpg',
  'National Museum of Yaoundé': '/images/destinations/real/national-museum-yaounde.jpg',
  'Waza National Park': '/images/destinations/real/waza-national-park.jpg',
  'Kribi Beachfront': '/images/destinations/real/kribi-beachfront.jpg',
  'Lobé Waterfalls': '/images/destinations/real/lobe-waterfalls.jpg',
  'Douala Night Market': '/images/destinations/real/douala-night-market.jpg',
  'Limbe Botanical Gardens': '/images/destinations/real/limbe-botanical-gardens.jpg',
  'Ekom Nkam Waterfalls': '/images/destinations/real/ekom-nkam-waterfalls.jpg',
  'Bafoussam Chiefdom Route': '/images/destinations/real/bafoussam-chiefdom-route.jpg',
  'Buea Mountain Loop': '/images/destinations/real/buea-mountain-loop.jpg',
  'Mfoundi Market Circuit': '/images/destinations/real/mfoundi-market-circuit.jpg',
  'Bamenda Highlands': '/images/destinations/real/bamenda-highlands.jpg',
}

const route = useRoute()
const router = useRouter()
const id = route.params.id
const destination = ref(null)
const loading = ref(true)
const error = ref(null)
const selectedImage = ref(null)

const mainImage = computed(() => {
  if (destination.value?.media?.main) return destination.value.media.main
  if (destination.value?.name && imageByName[destination.value.name]) return imageByName[destination.value.name]
  return null
})

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

function openImage(image) {
  selectedImage.value = image
}

function closeImage() {
  selectedImage.value = null
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
          <img :src="selectedImage" alt="Expanded media" class="max-h-[80vh] w-full rounded-2xl object-contain shadow-2xl" />
        </div>
      </div>
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

        <div class="mt-6 rounded-2xl border border-border-light bg-cream/70 p-5">
          <h2 class="text-lg font-semibold text-deep-blue">Why visit this place</h2>
          <p class="mt-2 text-sm leading-7 text-text-secondary">
            {{ destination.full_description || destination.description || 'Discover this destination through its atmosphere, activities, and local character.' }}
          </p>
        </div>

        <div class="mt-6 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div class="md:col-span-2">
            <div v-if="mainImage" class="overflow-hidden rounded-2xl border border-border-light bg-cream shadow-sm">
              <img
                :src="mainImage"
                alt="main media"
                class="h-80 w-full cursor-zoom-in object-cover transition duration-200 hover:scale-[1.01]"
                @click="openImage(mainImage)"
              />
            </div>
            <div v-else class="w-full h-64 rounded-lg bg-paper-dim flex items-center justify-center text-slate">No media available</div>

            <div v-if="destination.media && destination.media.secondary && destination.media.secondary.length" class="mt-4 grid grid-cols-3 gap-2">
              <img
                v-for="(s, idx) in destination.media.secondary"
                :key="idx"
                :src="s"
                class="h-20 w-full cursor-zoom-in rounded object-cover"
                @click="openImage(s)"
              />
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
                <InteractiveMap
                  v-if="destination.latitude && destination.longitude"
                  :items="[destination]"
                  :center="[destination.latitude, destination.longitude]"
                  :show-user-location="false"
                  visible
                  compact
                  allow-expand
                  title="Destination location"
                />
                <div v-else class="h-40 w-full rounded bg-paper-dim flex items-center justify-center text-slate">No map available</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
