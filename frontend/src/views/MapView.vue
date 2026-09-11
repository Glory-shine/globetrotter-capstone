<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import backgroundDestination from '../assets/images/backgrounds/background_destination.jpg'
import { searchDestinations } from '../api/destinations'
import { getFareEstimate } from '../api/fare'
import { destinationsCache } from '../stores/destinationsCache'
import { CATEGORY_EMOJIS, BAFOUSSAM_CENTER } from '../config'

const allDestinations = ref([])
const loading = ref(true)
const mapContainer = ref(null)
const map = ref(null)
const markersLayer = ref(null)
const routeLine = ref(null)
const mapReady = ref(false)

const placeQuery = ref('')
const placeSearchError = ref('')

const originId = ref('')
const arrivalId = ref('')
const mode = ref('taxi')
const fareResult = ref(null)
const fareLoading = ref(false)
const fareError = ref('')

const CATEGORY_COLORS = {
  Chefferie: '#c1502e',
  Musée: '#1f3b57',
  Marché: '#c89b3c',
  Nature: '#3f7d4f',
  Culture: '#8a4b8f',
  Hôtel: '#2f7a9c',
  Restaurant: '#d1642f',
  Institution: '#5c6b73',
  Hôpital: '#c0392b',
  Pharmacie: '#16a085',
  École: '#e67e22',
  Lycée: '#8e44ad',
  Université: '#2c3e50',
}
const DEFAULT_COLOR = '#c1502e'

// Filtre par catégorie : les lieux affichés sur la carte (et leurs
// marqueurs) peuvent être limités à un sous-ensemble de catégories —
// écoles, pharmacies, hôpitaux, lieux touristiques, etc.
const activeCategories = ref(new Set())
const availableCategories = computed(() => {
  const set = new Set(allDestinations.value.map((d) => d.category).filter(Boolean))
  return [...set].sort((a, b) => a.localeCompare(b))
})
const visibleDestinations = computed(() =>
  allDestinations.value.filter((d) => activeCategories.value.has(d.category)),
)
const allCategoriesActive = computed(
  () => activeCategories.value.size > 0 && activeCategories.value.size === availableCategories.value.length,
)

function toggleCategory(cat) {
  const next = new Set(activeCategories.value)
  if (next.has(cat)) {
    next.delete(cat)
  } else {
    next.add(cat)
  }
  activeCategories.value = next
}

function selectAllCategories() {
  activeCategories.value = new Set(availableCategories.value)
}

function selectNoCategories() {
  activeCategories.value = new Set()
}

const sorted = computed(() => [...allDestinations.value].sort((a, b) => a.name.localeCompare(b.name)))
const originOptions = computed(() => sorted.value.filter((d) => d.id !== arrivalId.value))
const arrivalOptions = computed(() => sorted.value.filter((d) => d.id !== originId.value))

const originDest = computed(() => allDestinations.value.find((d) => d.id === originId.value) || null)
const arrivalDest = computed(() => allDestinations.value.find((d) => d.id === arrivalId.value) || null)

function destColor(item) {
  return CATEGORY_COLORS[item?.category] || DEFAULT_COLOR
}

function markerIcon(item, big = false) {
  const size = big ? 34 : 26
  const color = destColor(item)
  const emoji = CATEGORY_EMOJIS[item?.category] || '📍'
  return window.L.divIcon({
    html: `
      <div style="
        width:${size}px; height:${size}px; border-radius:50% 50% 50% 0;
        background:${color}; transform: rotate(-45deg);
        border:2px solid white; box-shadow:0 3px 10px rgba(0,0,0,.35);
        display:flex; align-items:center; justify-content:center;
      ">
        <span style="transform: rotate(45deg); font-size:${big ? 16 : 13}px; line-height:1;">${emoji}</span>
      </div>
    `,
    className: '',
    iconSize: [size, size],
    iconAnchor: [size / 2, size],
    popupAnchor: [0, -size],
  })
}

function escapeHtml(str) {
  return String(str || '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c])
}

function popupHtml(item) {
  const img = item?.media?.main
  const price = item.price_range_xaf || (item.avg_cost_per_day ? `${Number(item.avg_cost_per_day).toLocaleString('fr-FR')} FCFA` : 'Gratuit')
  const rating = item.rating ? `${Number(item.rating).toFixed(1)} / 5` : '—'
  const desc = (item.description || '').slice(0, 130)
  return `
    <div style="width:230px; font-family: 'Plus Jakarta Sans', sans-serif; color:#22303b;">
      ${img ? `<img src="${img}" alt="${escapeHtml(item.name)}" style="width:100%; height:110px; object-fit:cover; border-radius:10px; margin-bottom:8px; display:block;" />` : ''}
      <div style="font-size:10px; font-weight:700; letter-spacing:.15em; text-transform:uppercase; color:${destColor(item)}; margin-bottom:3px;">
        ${escapeHtml(item.category || 'Lieu')}
      </div>
      <div style="font-size:15px; font-weight:700; margin-bottom:4px; line-height:1.2;">${escapeHtml(item.name)}</div>
      <div style="font-size:12px; color:#5c6b63; margin-bottom:8px; line-height:1.4;">${escapeHtml(desc)}${desc.length === 130 ? '…' : ''}</div>
      <div style="display:flex; justify-content:space-between; gap:8px; font-size:12px; border-top:1px solid #efe8d8; padding-top:6px;">
        <span>⭐ ${rating}</span>
        <span style="font-weight:600;">${escapeHtml(String(price))}</span>
      </div>
    </div>
  `
}

function renderMarkers() {
  if (!map.value || !markersLayer.value) return
  markersLayer.value.clearLayers()
  const bounds = []
  visibleDestinations.value.forEach((item) => {
    if (!item.latitude || !item.longitude) return
    const marker = window.L.marker([item.latitude, item.longitude], { icon: markerIcon(item) })
    marker.bindPopup(popupHtml(item), { maxWidth: 260 })
    marker.addTo(markersLayer.value)
    bounds.push([item.latitude, item.longitude])
  })
  if (bounds.length && !originId.value && !arrivalId.value) {
    map.value.fitBounds(bounds, { padding: [32, 32] })
  }
}

function clearRoute() {
  if (routeLine.value && map.value) {
    routeLine.value.remove()
    routeLine.value = null
  }
}

function drawRoute() {
  clearRoute()
  if (!map.value || !originDest.value || !arrivalDest.value) return

  const from = [originDest.value.latitude, originDest.value.longitude]
  const to = [arrivalDest.value.latitude, arrivalDest.value.longitude]

  // Un groupe de calques pour le halo + le trait principal, afin de
  // pouvoir les ajouter/retirer ensemble proprement (L.polyline().addTo()
  // attend une carte ou un layer group, pas une autre polyline).
  routeLine.value = window.L.layerGroup([
    window.L.polyline([from, to], { color: '#c89b3c', weight: 9, opacity: 0.25 }),
    window.L.polyline([from, to], {
      color: '#c1502e',
      weight: 5,
      opacity: 0.9,
      dashArray: '2 10',
      lineCap: 'round',
    }),
  ]).addTo(map.value)

  map.value.fitBounds([from, to], { padding: [70, 70] })
}

async function estimateFare() {
  if (!originId.value || !arrivalId.value || originId.value === arrivalId.value) {
    fareResult.value = null
    drawRoute()
    return
  }
  fareLoading.value = true
  fareError.value = ''
  fareResult.value = null
  try {
    fareResult.value = await getFareEstimate({ fromId: originId.value, toId: arrivalId.value, mode: mode.value })
    drawRoute()
  } catch {
    fareError.value = "Impossible d'estimer le tarif pour le moment."
  } finally {
    fareLoading.value = false
  }
}

function swapPoints() {
  const tmp = originId.value
  originId.value = arrivalId.value
  arrivalId.value = tmp
}

function resetRoute() {
  originId.value = ''
  arrivalId.value = ''
  fareResult.value = null
  clearRoute()
  const bounds = visibleDestinations.value.filter((d) => d.latitude && d.longitude).map((d) => [d.latitude, d.longitude])
  if (bounds.length) map.value?.fitBounds(bounds, { padding: [32, 32] })
}

async function searchPlace(event) {
  event?.preventDefault()
  const query = placeQuery.value.trim()
  placeSearchError.value = ''
  if (!query) return

  const match = allDestinations.value.find((d) => d.name.toLowerCase().includes(query.toLowerCase()))
  if (match) {
    map.value?.flyTo([match.latitude, match.longitude], 15)
    markersLayer.value?.eachLayer((layer) => {
      if (layer.getLatLng && layer.getLatLng().lat === match.latitude && layer.getLatLng().lng === match.longitude) {
        layer.openPopup()
      }
    })
    return
  }

  try {
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query + ', Bafoussam, Cameroun')}`)
    const results = await response.json()
    const place = results?.[0]
    if (!place) {
      placeSearchError.value = 'Aucun lieu trouvé.'
      return
    }
    map.value?.flyTo([Number(place.lat), Number(place.lon)], 14)
  } catch {
    placeSearchError.value = 'Recherche indisponible pour le moment.'
  }
}

function initMap() {
  if (!mapContainer.value || typeof window === 'undefined' || !window.L) return
  map.value = window.L.map(mapContainer.value, { zoomControl: true, scrollWheelZoom: true }).setView(BAFOUSSAM_CENTER, 14)
  window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map.value)
  markersLayer.value = window.L.layerGroup().addTo(map.value)
  mapReady.value = true
  nextTick(renderMarkers)
}

async function loadDestinations() {
  loading.value = true
  try {
    const data = await searchDestinations({})
    allDestinations.value = data
    destinationsCache.cache(data)
    selectAllCategories()
  } catch {
    // toast handled globally
  } finally {
    loading.value = false
    nextTick(renderMarkers)
  }
}

watch([originId, arrivalId, mode], estimateFare)
watch(activeCategories, () => nextTick(renderMarkers))

onMounted(async () => {
  await loadDestinations()
  nextTick(initMap)
})

onBeforeUnmount(() => {
  if (map.value) {
    map.value.remove()
    map.value = null
    markersLayer.value = null
  }
})
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-10"
      :style="{ backgroundImage: `url(${backgroundDestination})` }"
    />
    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Carte interactive</p>
        <h1 class="mt-3 font-display text-5xl font-semibold text-deep-blue sm:text-6xl">Tous les lieux de Bafoussam</h1>
        <p class="mt-3 text-lg leading-relaxed text-text-secondary">
          Explorez chefferies, marchés, hôtels, restaurants et institutions sur la carte, et estimez
          directement le tarif moto-taxi ou taxi entre deux lieux.
        </p>
      </div>
      <div class="bamileke-band mt-6 max-w-2xl rounded-full" />

      <div class="mt-10 overflow-hidden rounded-3xl border border-border-light bg-white/80 shadow-xl backdrop-blur-xl">
        <!-- Barre d'outils intégrée à la carte : recherche + estimation de tarif -->
        <div class="border-b border-border-light bg-white/90 p-5 sm:p-6">
          <form class="flex flex-col gap-2 sm:flex-row" @submit="searchPlace">
            <div class="relative flex-1">
              <svg class="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-text-light" viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2" />
                <path d="m20 20-3.5-3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
              <input
                v-model="placeQuery"
                type="text"
                placeholder="Rechercher un lieu sur la carte…"
                class="w-full rounded-2xl border border-border-light bg-cream py-3 pl-12 pr-4 text-sm text-text-primary outline-none transition focus:border-sage focus:ring-2 focus:ring-sage/20"
              />
            </div>
            <button type="submit" class="rounded-2xl bg-deep-blue px-6 py-3 text-sm font-semibold text-white transition hover:bg-sage">
              Rechercher
            </button>
          </form>
          <p v-if="placeSearchError" class="mt-2 text-xs text-sage">{{ placeSearchError }}</p>

          <div class="mt-4 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-text-secondary">
            <span
              v-for="(color, cat) in CATEGORY_COLORS"
              :key="cat"
              class="inline-flex items-center gap-1.5"
            >
              <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: color }" />
              {{ cat }}
            </span>
          </div>

          <!-- Filtre par catégorie : limite les lieux affichés sur la carte -->
          <div class="mt-4 border-t border-border-light pt-4">
            <div class="mb-2 flex items-center justify-between">
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-text-light">Filtrer la carte</p>
              <div class="flex gap-3 text-xs">
                <button type="button" class="font-medium text-sage hover:underline" @click="selectAllCategories">Tout afficher</button>
                <button type="button" class="font-medium text-text-light hover:underline" @click="selectNoCategories">Tout masquer</button>
              </div>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="cat in availableCategories"
                :key="cat"
                type="button"
                class="rounded-full border-2 px-3 py-1.5 text-xs font-medium transition"
                :class="
                  activeCategories.has(cat)
                    ? 'border-sage bg-sage/10 text-sage'
                    : 'border-border-light bg-white text-text-light hover:border-sage hover:text-sage'
                "
                @click="toggleCategory(cat)"
              >
                <span class="mr-1.5">{{ CATEGORY_EMOJIS[cat] || '📍' }}</span>{{ cat }}
              </button>
            </div>
            <p class="mt-2 text-xs text-text-light">
              {{ visibleDestinations.length }} / {{ allDestinations.length }} lieux affichés{{ allCategoriesActive ? '' : ' (filtré)' }}
            </p>
          </div>
        </div>

        <!-- Estimation de tarif, intégrée directement à la carte -->
        <div class="border-b border-border-light bg-deep-blue p-5 text-cream sm:p-6">
          <div class="flex items-center gap-2">
            <span class="text-lg">🏍️</span>
            <h3 class="font-display text-lg font-semibold">Estimer un trajet sur la carte</h3>
          </div>
          <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto_1fr_auto] sm:items-end">
            <div>
              <label class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-cream/70">Départ</label>
              <select
                v-model="originId"
                class="w-full rounded-xl border border-cream/20 bg-cream/5 px-3 py-2.5 text-sm text-cream outline-none focus:border-sage focus:ring-2 focus:ring-sage/30"
              >
                <option value="" disabled class="text-text-primary">Choisir un lieu…</option>
                <option v-for="d in originOptions" :key="d.id" :value="d.id" class="text-text-primary">{{ d.name }}</option>
              </select>
            </div>
            <button
              type="button"
              class="mx-auto grid h-9 w-9 place-items-center rounded-full border border-cream/20 bg-cream/5 text-cream transition hover:border-sage hover:text-sage sm:mb-0.5"
              title="Inverser départ / arrivée"
              aria-label="Inverser départ et arrivée"
              @click="swapPoints"
            >
              ⇄
            </button>
            <div>
              <label class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-cream/70">Arrivée</label>
              <select
                v-model="arrivalId"
                class="w-full rounded-xl border border-cream/20 bg-cream/5 px-3 py-2.5 text-sm text-cream outline-none focus:border-sage focus:ring-2 focus:ring-sage/30"
              >
                <option value="" disabled class="text-text-primary">Choisir un lieu…</option>
                <option v-for="d in arrivalOptions" :key="d.id" :value="d.id" class="text-text-primary">{{ d.name }}</option>
              </select>
            </div>
            <div class="flex gap-2 sm:mb-0.5">
              <button
                type="button"
                class="rounded-xl border-2 px-3 py-2.5 text-sm font-medium transition"
                :class="mode === 'moto' ? 'border-sage bg-sage text-white' : 'border-cream/20 text-cream hover:border-sage'"
                @click="mode = 'moto'"
              >
                🏍️
              </button>
              <button
                type="button"
                class="rounded-xl border-2 px-3 py-2.5 text-sm font-medium transition"
                :class="mode === 'taxi' ? 'border-sage bg-sage text-white' : 'border-cream/20 text-cream hover:border-sage'"
                @click="mode = 'taxi'"
              >
                🚕
              </button>
            </div>
          </div>

          <div v-if="originId && arrivalId && originId === arrivalId" class="mt-3 text-sm text-sage-light">
            Choisissez deux lieux différents pour estimer le trajet.
          </div>
          <div v-else-if="fareLoading" class="mt-3 animate-pulse text-sm text-cream/60">Calcul de l'estimation…</div>
          <p v-else-if="fareError" class="mt-3 text-sm text-sage-light">{{ fareError }}</p>
          <div v-else-if="fareResult" class="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-cream/15 bg-cream/5 px-4 py-3">
            <div>
              <p class="text-xs uppercase tracking-[0.2em] text-cream/50">{{ fareResult.from_name }} → {{ fareResult.to_name }}</p>
              <p class="text-xs text-cream/60">{{ fareResult.distance_km }} km · ~{{ fareResult.duration_min }} min · trajet surligné sur la carte</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="font-display text-2xl font-semibold">{{ fareResult.price_label }}</span>
              <button type="button" class="text-xs font-medium text-cream/70 underline-offset-2 hover:underline" @click="resetRoute">
                Effacer
              </button>
            </div>
          </div>
        </div>

        <!-- La carte elle-même -->
        <div class="relative h-[70vh] min-h-[420px] w-full">
          <div v-if="loading || !mapReady" class="absolute inset-0 z-[400] flex items-center justify-center bg-cream/70">
            <div class="animate-pulse text-sm text-text-secondary">Chargement de la carte…</div>
          </div>
          <div ref="mapContainer" class="h-full w-full" />
        </div>
      </div>
    </div>
  </div>
</template>
