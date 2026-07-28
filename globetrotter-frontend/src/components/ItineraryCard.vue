<script setup>
import { computed, ref } from 'vue'
import { deleteItinerary, updateItinerary } from '../api/itineraries'
import { toastStore } from '../stores/toast'

const props = defineProps({
  itinerary: { type: Object, required: true },
  destination: { type: Object, default: null },
  destinations: { type: Array, default: () => [] },
})

const emit = defineEmits(['updated', 'deleted'])
const editing = ref(false)
const form = ref({
  title: props.itinerary.title || '',
  destination_id: props.itinerary.destination_id || '',
  start_date: props.itinerary.start_date || '',
  end_date: props.itinerary.end_date || '',
  items: (props.itinerary.items || []).map((item) => ({ ...item })),
})

const sortedItems = computed(() =>
  [...(props.itinerary.items || [])].sort((a, b) => a.day - b.day)
)

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

const imageSrc = computed(() => {
  if (props.destination?.media?.main) return props.destination.media.main
  if (props.destination?.name && imageByName[props.destination.name]) return imageByName[props.destination.name]
  return null
})

const tripLength = computed(() => {
  const start = new Date(props.itinerary.start_date)
  const end = new Date(props.itinerary.end_date)
  return Math.round((end - start) / 86400000) + 1
})

async function share() {
  const destName = props.destination ? `${props.destination.name}, ${props.destination.country}` : 'TBD'
  const lines = [
    `✈ ${props.itinerary.title}`,
    `${destName} · ${props.itinerary.start_date} → ${props.itinerary.end_date}`,
    ...sortedItems.value.map((i) => `  Day ${i.day}: ${i.activity}`),
  ]
  const text = lines.join('\n')

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      toastStore.success('Itinerary copied — ready to share.')
    } else {
      throw new Error('Clipboard unavailable')
    }
  } catch {
    toastStore.info(text)
  }
}

function startEdit() {
  editing.value = true
  form.value = {
    title: props.itinerary.title || '',
    destination_id: props.itinerary.destination_id || '',
    start_date: props.itinerary.start_date || '',
    end_date: props.itinerary.end_date || '',
    items: (props.itinerary.items || []).map((item) => ({ ...item })),
  }
}

function cancelEdit() {
  editing.value = false
}

function addItem() {
  const nextDay = form.value.items.length ? Math.max(...form.value.items.map((item) => Number(item.day) || 0)) + 1 : 1
  form.value.items.push({ day: nextDay, activity: '' })
}

function removeItem(index) {
  form.value.items.splice(index, 1)
}

async function saveEdit() {
  try {
    const updated = await updateItinerary(props.itinerary.id, {
      title: form.value.title.trim(),
      destination_id: form.value.destination_id,
      start_date: form.value.start_date,
      end_date: form.value.end_date,
      items: form.value.items.filter((item) => item.activity?.trim()).map((item) => ({ day: Number(item.day), activity: item.activity.trim() })),
    })
    toastStore.success('Itinerary updated.')
    emit('updated', updated)
    editing.value = false
  } catch {
    // interceptor already surfaced a toast
  }
}

async function removeItinerary() {
  try {
    await deleteItinerary(props.itinerary.id)
    toastStore.success('Itinerary deleted.')
    emit('deleted', props.itinerary.id)
  } catch {
    // interceptor already surfaced a toast
  }
}
</script>

<template>
  <article class="overflow-hidden rounded-2xl border border-ink/10 bg-white/60 shadow-sm shadow-ink/5">
    <div v-if="imageSrc" class="h-40 overflow-hidden bg-cream">
      <img :src="imageSrc" :alt="`${destination?.name || 'Destination'} image`" class="h-full w-full object-cover" />
    </div>

    <div class="p-6">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 class="font-display text-lg font-semibold text-ink">{{ itinerary.title }}</h3>
          <p class="font-mono text-xs uppercase tracking-wide text-slate">
            {{ destination ? `${destination.name}, ${destination.country}` : 'Destination unavailable' }}
          </p>
        </div>
        <span class="stamp rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider">
          {{ tripLength }} day{{ tripLength === 1 ? '' : 's' }}
        </span>
      </div>

      <p class="mt-1 font-mono text-xs text-slate">
        {{ itinerary.start_date }} → {{ itinerary.end_date }}
      </p>

      <div v-if="editing" class="mt-4 space-y-3 rounded-2xl border border-border-light bg-cream/50 p-4">
        <input v-model="form.title" class="w-full rounded-xl border border-border-light bg-white px-3 py-2 text-sm" placeholder="Title" />
        <select v-model="form.destination_id" class="w-full rounded-xl border border-border-light bg-white px-3 py-2 text-sm">
          <option value="" disabled>Select a destination</option>
          <option v-for="option in destinations" :key="option.id" :value="option.id">
            {{ option.name }}, {{ option.country }}
          </option>
        </select>
        <input v-model="form.start_date" type="date" class="w-full rounded-xl border border-border-light bg-white px-3 py-2 text-sm" />
        <input v-model="form.end_date" type="date" class="w-full rounded-xl border border-border-light bg-white px-3 py-2 text-sm" />

        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-text-primary">Day-by-day plan</span>
          <button type="button" class="text-xs font-medium text-sage" @click="addItem">+ Add a day</button>
        </div>

        <div v-for="(item, index) in form.items" :key="`${item.day}-${index}`" class="flex items-center gap-2">
          <input v-model.number="item.day" type="number" min="1" class="w-16 rounded-xl border border-border-light bg-white px-2 py-2 text-sm" />
          <input v-model="item.activity" class="flex-1 rounded-xl border border-border-light bg-white px-3 py-2 text-sm" placeholder="Plan item" />
          <button v-if="form.items.length > 1" type="button" class="text-sm text-coral" @click="removeItem(index)">✕</button>
        </div>

        <div class="flex gap-2">
          <button type="button" class="rounded-full bg-deep-blue px-3 py-2 text-sm text-white" @click="saveEdit">Save</button>
          <button type="button" class="rounded-full border border-border-light px-3 py-2 text-sm" @click="cancelEdit">Cancel</button>
        </div>
      </div>

      <div v-else>
        <div v-if="sortedItems.length" class="mt-5 space-y-5 pl-1">
          <div v-for="item in sortedItems" :key="item.day" class="relative flex gap-4 pb-1 pl-2">
            <div class="flex flex-col items-center">
              <span
                class="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-teal font-mono text-[11px] font-semibold text-paper"
              >
                {{ item.day }}
              </span>
              <span class="flight-path mt-1 w-px flex-1" />
            </div>
            <p class="pt-1 text-sm text-ink">{{ item.activity }}</p>
          </div>
        </div>
        <p v-else class="mt-5 text-sm italic text-slate">No day-by-day plan added yet.</p>
      </div>

      <div class="mt-5 flex flex-wrap gap-2">
        <button
          type="button"
          class="flex items-center gap-1.5 rounded-full border border-ink/15 px-3.5 py-1.5 text-xs font-medium text-ink transition hover:border-coral hover:text-coral"
          @click="share"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7M16 6l-4-4-4 4M12 2v14"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          Share
        </button>
        <button type="button" class="rounded-full border border-border-light px-3.5 py-1.5 text-xs font-medium text-deep-blue" @click="startEdit">
          Edit
        </button>
        <button type="button" class="rounded-full border border-coral/30 px-3.5 py-1.5 text-xs font-medium text-coral" @click="removeItinerary">
          Delete
        </button>
      </div>
    </div>
  </article>
</template>
