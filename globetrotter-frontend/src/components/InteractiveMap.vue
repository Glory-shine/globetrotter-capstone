<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  activeCategory: { type: String, default: 'all' },
  visible: { type: Boolean, default: true },
  title: { type: String, default: 'Places' },
  center: { type: Array, default: () => [4.0, 11.5] },
})

const mapContainer = ref(null)
const map = ref(null)
const markersLayer = ref(null)
const mapLoading = ref(true)
const userLocation = ref(null)

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
      if (popup) popup.setContent(createPopup(item))
    })
    marker.addTo(markersLayer.value)
    bounds.push([item.latitude, item.longitude])
  })

  if (bounds.length) {
    map.value.fitBounds(bounds, { padding: [24, 24] })
  }

  mapLoading.value = false
}

function initMap() {
  if (!mapContainer.value || map.value || typeof window === 'undefined' || !window.L) return

  map.value = window.L.map(mapContainer.value, {
    zoomControl: true,
    scrollWheelZoom: false,
  }).setView(props.center, 5)

  window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map.value)

  markersLayer.value = window.L.layerGroup().addTo(map.value)

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userLocation.value = [position.coords.latitude, position.coords.longitude]
        window.L.marker(userLocation.value, {
          icon: window.L.divIcon({
            html: '<div style="width:16px;height:16px;border-radius:999px;background:#1e7f76;border:2px solid white;box-shadow:0 3px 8px rgba(0,0,0,.25);"></div>',
            className: '',
            iconSize: [16, 16],
            iconAnchor: [8, 8],
          }),
        })
          .addTo(markersLayer.value)
          .bindPopup('Your current location')
        map.value.setView(userLocation.value, 8)
      },
      () => {},
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
</script>

<template>
  <div class="rounded-3xl border border-ink/10 bg-white/80 p-4 shadow-sm shadow-ink/5">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <p class="font-mono text-[11px] uppercase tracking-[0.3em] text-teal">{{ title }}</p>
        <p class="text-sm text-slate">Tap a pin for pricing, rating, and local context.</p>
      </div>
      <div class="rounded-full bg-paper-dim px-3 py-1 text-xs font-medium text-ink">
        {{ filteredItems.length }} active spots
      </div>
    </div>

    <div v-if="visible" class="h-[360px] overflow-hidden rounded-2xl border border-ink/10">
      <div v-if="mapLoading" class="flex h-full items-center justify-center bg-paper-dim">
        <div class="animate-pulse text-sm text-slate">Loading map pins…</div>
      </div>
      <div ref="mapContainer" class="h-full w-full" />
    </div>
  </div>
</template>
