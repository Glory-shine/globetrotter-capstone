<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  activeCategory: { type: String, default: 'all' },
  visible: { type: Boolean, default: true },
  title: { type: String, default: 'Places' },
  center: { type: Array, default: () => [4.0, 11.5] },
  showUserLocation: { type: Boolean, default: true },
  compact: { type: Boolean, default: false },
  allowExpand: { type: Boolean, default: false },
})

const mapContainer = ref(null)
const expandedMapContainer = ref(null)
const map = ref(null)
const markersLayer = ref(null)
const mapLoading = ref(true)
const userLocation = ref(null)
const searchQuery = ref('')
const searchError = ref('')
const selectedItem = ref(null)
const searchResultMarker = ref(null)
const locationStatus = ref('')
const compactSearchOpen = ref(false)
const expanded = ref(false)

const filteredItems = computed(() =>
  (props.items || []).filter((item) => {
    if (!item || !item.latitude || !item.longitude) return false
    if (props.activeCategory === 'all') return true

    const category = (item.category || '').toLowerCase()
    const tags = (item.tags || []).map((tag) => String(tag).toLowerCase())
    const normalized = props.activeCategory

    if (normalized === 'food') {
      return category === 'food' || tags.some((tag) => ['food', 'restaurant', 'market', 'boukarou'].includes(tag))
    }
    if (normalized === 'culture') {
      return category === 'culture' || tags.some((tag) => ['culture', 'history', 'museum', 'chiefdom', 'chefferie'].includes(tag))
    }
    if (normalized === 'nature') {
      return category === 'nature' || tags.some((tag) => ['nature', 'adventure', 'park', 'waterfall', 'beach', 'ecotourism'].includes(tag))
    }
    if (normalized === 'nightlife') {
      return category === 'nightlife' || tags.some((tag) => ['nightlife', 'lounge', 'cabaret'].includes(tag))
    }

    return category === normalized || tags.includes(normalized)
  }),
)

function createPopup(item) {
  const price = item.price_range_xaf || `${item.avg_cost_per_day?.toLocaleString() || 0} XAF`
  const rating = item.rating ? `${item.rating.toFixed(1)} / 5` : 'New'
  const category = item.category ? item.category : 'spot'

  return `
    <div style="min-width:190px; font-family: Inter, sans-serif; color:#0e2a3f;">
      <div style="font-size:12px; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:#1e7f76; margin-bottom:4px;">${category}</div>
      <div style="font-size:16px; font-weight:700; margin-bottom:6px;">${item.name}</div>
      <div style="font-size:13px; color:#5b6b76; margin-bottom:8px;">${item.description || ''}</div>
      <div style="display:flex; justify-content:space-between; gap:10px; font-size:13px;">
        <span><strong>⭐</strong> ${rating}</span>
        <span><strong>₣</strong> ${price}</span>
      </div>
    </div>
  `
}

function toRad(value) {
  return (value * Math.PI) / 180
}

function calculateDistanceKm(from, to) {
  if (!from || !to) return null
  const earthRadiusKm = 6371
  const dLat = toRad(to[0] - from[0])
  const dLon = toRad(to[1] - from[1])
  const lat1 = toRad(from[0])
  const lat2 = toRad(to[0])
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return earthRadiusKm * c
}

function formatDistance(distanceKm) {
  if (distanceKm === null || distanceKm === undefined) return 'Distance unavailable'
  return `${distanceKm.toFixed(1)} km`
}

function formatTime(distanceKm) {
  if (distanceKm === null || distanceKm === undefined) return 'Travel time unavailable'
  const minutes = Math.max(1, Math.round((distanceKm / 40) * 60))
  return `${minutes} min`
}

function setSelectedItem(item) {
  selectedItem.value = item
}

async function reverseGeocodeName(lat, lon) {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&zoom=16&accept-language=fr`,
    )
    const place = await response.json()
    if (!place || place.error) return null
    const addr = place.address || {}
    return (
      addr.suburb || addr.neighbourhood || addr.quarter || addr.village || addr.town || addr.city_district ||
      addr.city || place.display_name || null
    )
  } catch {
    return null
  }
}

function goToCurrentLocation() {
  if (!map.value || !navigator.geolocation) {
    locationStatus.value = "La géolocalisation n'est pas disponible sur ce navigateur."
    return
  }

  locationStatus.value = 'Recherche de votre position…'

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const nextLocation = [position.coords.latitude, position.coords.longitude]
      userLocation.value = nextLocation
      map.value.setView(nextLocation, 14)

      const placeName = await reverseGeocodeName(nextLocation[0], nextLocation[1])
      locationStatus.value = placeName
        ? `Vous êtes ici, près de : ${placeName}`
        : 'Position actuelle mise à jour.'

      if (markersLayer.value) {
        const marker = window.L.marker(nextLocation, {
          icon: window.L.divIcon({
            html: '<div style="width:16px;height:16px;border-radius:999px;background:#1e7f76;border:2px solid white;box-shadow:0 3px 8px rgba(0,0,0,.25);"></div>',
            className: '',
            iconSize: [16, 16],
            iconAnchor: [8, 8],
          }),
        })
        marker.addTo(markersLayer.value).bindPopup(placeName ? `Vous êtes ici, près de : ${placeName}` : 'Votre position actuelle').openPopup()
      }
    },
    (error) => {
      if (error.code === 1) {
        locationStatus.value = "Accès à la position refusé — merci d'autoriser la géolocalisation dans votre navigateur."
      } else {
        locationStatus.value = 'Impossible de récupérer votre position pour le moment.'
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    },
  )
}

function toggleCompactSearch() {
  compactSearchOpen.value = !compactSearchOpen.value
  searchError.value = ''
}

function toggleExpanded() {
  expanded.value = !expanded.value
  if (expanded.value) {
    nextTick(() => {
      map.value?.invalidateSize()
    })
  }
}

async function searchLocation(event) {
  event?.preventDefault()
  const query = searchQuery.value.trim()
  if (!query) return

  searchError.value = ''

  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query)}`)
    const results = await response.json()
    const place = results?.[0]

    if (!place) {
      searchError.value = 'No matching place found.'
      return
    }

    const lat = Number(place.lat)
    const lon = Number(place.lon)

    if (searchResultMarker.value && markersLayer.value) {
      markersLayer.value.removeLayer(searchResultMarker.value)
    }

    searchResultMarker.value = window.L.marker([lat, lon], {
      icon: window.L.divIcon({
        html: '<div style="width:14px;height:14px;background:#1e7f76;border:2px solid white;border-radius:999px;box-shadow:0 3px 8px rgba(0,0,0,.25);"></div>',
        className: '',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      }),
    })

    searchResultMarker.value.bindPopup(`Searched place: ${place.display_name}`)
    searchResultMarker.value.addTo(markersLayer.value)
    setSelectedItem({ name: place.display_name, latitude: lat, longitude: lon, description: 'Searched location' })
    map.value?.flyTo([lat, lon], 12)
  } catch {
    searchError.value = 'Unable to search this place right now.'
  }
}

function renderMarkers() {
  if (!map.value || !markersLayer.value) return
  markersLayer.value.clearLayers()

  if (!filteredItems.value.length) {
    mapLoading.value = false
    return
  }

  const bounds = []
  filteredItems.value.forEach((item) => {
    const marker = window.L.marker([item.latitude, item.longitude], {
      icon: window.L.divIcon({
        html: '<div style="width:14px;height:14px;background:#ff6b4a;border:2px solid white;border-radius:999px;box-shadow:0 3px 8px rgba(0,0,0,.25);"></div>',
        className: '',
        iconSize: [14, 14],
        iconAnchor: [7, 7],
      }),
    })

    marker.bindPopup(createPopup(item))
    marker.on('click', () => {
      const popup = marker.getPopup()
      setSelectedItem(item)
      if (popup) popup.setContent(createPopup(item))
    })
    marker.addTo(markersLayer.value)
    bounds.push([item.latitude, item.longitude])
  })

  if (!selectedItem.value && filteredItems.value.length === 1) {
    setSelectedItem(filteredItems.value[0])
  }

  if (bounds.length) {
    map.value.fitBounds(bounds, { padding: [24, 24] })
  }

  mapLoading.value = false
}

function initMap() {
  const containerRef = expanded.value ? expandedMapContainer.value : mapContainer.value
  if (!containerRef || typeof window === 'undefined' || !window.L) return

  if (map.value) {
    map.value.remove()
    map.value = null
    markersLayer.value = null
  }

  map.value = window.L.map(containerRef, {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView(props.center, 5)

  window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map.value)

  markersLayer.value = window.L.layerGroup().addTo(map.value)

  if (props.showUserLocation && navigator.geolocation) {
    locationStatus.value = 'Recherche de votre position…'
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        userLocation.value = [position.coords.latitude, position.coords.longitude]
        map.value.setView(userLocation.value, 14)

        const placeName = await reverseGeocodeName(userLocation.value[0], userLocation.value[1])
        locationStatus.value = placeName
          ? `Vous êtes ici, près de : ${placeName}`
          : 'Position actuelle mise à jour.'

        window.L.marker(userLocation.value, {
          icon: window.L.divIcon({
            html: '<div style="width:16px;height:16px;border-radius:999px;background:#1e7f76;border:2px solid white;box-shadow:0 3px 8px rgba(0,0,0,.25);"></div>',
            className: '',
            iconSize: [16, 16],
            iconAnchor: [8, 8],
          }),
        })
          .addTo(markersLayer.value)
          .bindPopup(placeName ? `Vous êtes ici, près de : ${placeName}` : 'Votre position actuelle')
      },
      (error) => {
        if (error.code === 1) {
          locationStatus.value = "Accès à la position refusé — merci d'autoriser la géolocalisation dans votre navigateur."
        } else {
          locationStatus.value = 'Impossible de récupérer votre position pour le moment.'
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      },
    )
  }

  nextTick(() => {
    renderMarkers()
  })
}

watch(
  () => props.items,
  () => {
    nextTick(() => renderMarkers())
  },
  { deep: true },
)

watch(
  () => props.activeCategory,
  () => {
    nextTick(() => renderMarkers())
  },
)

watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      nextTick(() => initMap())
    }
  },
)

watch(expanded, (isExpanded) => {
  if (props.visible) {
    nextTick(() => initMap())
  }
})

onMounted(() => {
  if (props.visible) {
    nextTick(() => initMap())
  }
})

onBeforeUnmount(() => {
  if (map.value) {
    map.value.remove()
    map.value = null
    markersLayer.value = null
  }
})

const distanceKm = computed(() => {
  if (!userLocation.value || !selectedItem.value) return null
  return calculateDistanceKm(userLocation.value, [selectedItem.value.latitude, selectedItem.value.longitude])
})
</script>

<template>
  <div class="rounded-3xl border border-ink/10 bg-white/80 p-4 shadow-sm shadow-ink/5">
    <div class="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div>
        <p class="font-mono text-[11px] uppercase tracking-[0.3em] text-teal">{{ title }}</p>
        <p class="text-sm text-slate">Search a place directly on the map and compare it to your current location.</p>
      </div>
      <div
        class="flex w-full flex-wrap items-center gap-2 md:w-auto"
        :class="{ 'justify-end': props.compact }">
        <template v-if="props.compact">
          <button
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-border-light bg-white text-deep-blue shadow-sm transition hover:bg-sage/10"
            @click="toggleCompactSearch"
            aria-label="Search"
          >
            🔍
          </button>
          <button
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-border-light bg-white text-deep-blue shadow-sm transition hover:bg-sage/10"
            @click="goToCurrentLocation"
            aria-label="My localisation"
          >
            📍
          </button>
          <button
            v-if="props.allowExpand"
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-border-light bg-white text-deep-blue shadow-sm transition hover:bg-sage/10"
            @click="toggleExpanded"
            :aria-label="expanded ? 'Close expanded map' : 'Expand map'"
          >
            {{ expanded ? '✕' : '⤢' }}
          </button>
        </template>

        <template v-else>
          <form class="flex items-center gap-2" @submit="searchLocation">
            <input
              v-model="searchQuery"
              type="text"
              class="w-full rounded-full border border-border-light bg-paper-dim px-3 py-2 text-sm text-ink outline-none focus:border-teal md:w-64"
              placeholder="Search a place"
            />
            <button type="submit" class="rounded-full bg-deep-blue px-3 py-2 text-sm font-medium text-white">
              Search
            </button>
          </form>
          <button type="button" class="rounded-full border border-border-light bg-white px-3 py-2 text-sm font-medium text-deep-blue" @click="goToCurrentLocation">
            My localisation
          </button>
        </template>
      </div>
    </div>

    <div v-if="props.compact && compactSearchOpen" class="mb-3 rounded-2xl border border-border-light bg-white/90 p-3 shadow-sm">
      <form class="flex items-center gap-2" @submit="searchLocation">
        <input
          v-model="searchQuery"
          type="text"
          class="w-full rounded-full border border-border-light bg-paper-dim px-3 py-2 text-sm text-ink outline-none focus:border-teal"
          placeholder="Search a place"
        />
        <button type="submit" class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-deep-blue text-white">
          🔍
        </button>
      </form>
    </div>

    <p v-if="searchError" class="mb-3 text-sm text-coral">{{ searchError }}</p>
    <p v-if="locationStatus" class="mb-3 text-sm text-sage">{{ locationStatus }}</p>

    <div v-if="selectedItem && distanceKm !== null" class="mb-3 rounded-2xl border border-border-light bg-cream/70 p-3 text-sm text-text-secondary">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p class="font-semibold text-deep-blue">{{ selectedItem.name }}</p>
          <p class="text-xs uppercase tracking-[0.25em] text-sage">Current location comparison</p>
        </div>
        <div class="text-right">
          <p class="font-semibold text-deep-blue">{{ formatDistance(distanceKm) }}</p>
          <p class="text-xs text-slate">≈ {{ formatTime(distanceKm) }}</p>
        </div>
      </div>
    </div>

    <div v-if="visible" class="h-[360px] overflow-hidden rounded-2xl border border-ink/10">
      <div v-if="mapLoading" class="flex h-full items-center justify-center bg-paper-dim">
        <div class="animate-pulse text-sm text-slate">Loading map pins…</div>
      </div>
      <div v-show="!expanded" ref="mapContainer" class="h-full w-full" />
      <div v-if="expanded" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
        <div class="relative w-full max-w-4xl overflow-hidden rounded-3xl bg-white shadow-2xl">
          <div class="absolute right-3 top-3 flex items-center gap-2">
            <button
              type="button"
              class="inline-flex h-10 w-10 items-center justify-center rounded-full border border-border-light bg-white text-deep-blue shadow-sm transition hover:bg-sage/10"
              @click="toggleExpanded"
              aria-label="Close expanded map"
            >
              ✕
            </button>
          </div>
          <button
            type="button"
            class="absolute left-3 top-3 inline-flex items-center gap-2 rounded-full border border-border-light bg-white px-3 py-2 text-sm font-medium text-deep-blue shadow-sm transition hover:bg-sage/10"
            @click="toggleExpanded"
            aria-label="Retour à la vue détaillée"
          >
            ← Retour
          </button>
          <div class="h-[560px] w-full">
            <div ref="expandedMapContainer" class="h-full w-full" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
