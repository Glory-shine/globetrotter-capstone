<script setup>
import { computed } from 'vue'
import { toastStore } from '../stores/toast'

const props = defineProps({
  itinerary: { type: Object, required: true },
  destination: { type: Object, default: null },
})

const sortedItems = computed(() =>
  [...(props.itinerary.items || [])].sort((a, b) => a.day - b.day)
)

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
</script>

<template>
  <article class="rounded-2xl border border-ink/10 bg-white/60 p-6 shadow-sm shadow-ink/5">
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

    <!-- Flight-path timeline -->
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

    <button
      type="button"
      class="mt-5 flex items-center gap-1.5 rounded-full border border-ink/15 px-3.5 py-1.5 text-xs font-medium text-ink transition hover:border-coral hover:text-coral"
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
  </article>
</template>
