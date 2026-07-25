<script setup>
import { computed } from 'vue'

const props = defineProps({
  destination: { type: Object, required: true },
  matchTags: { type: Array, default: () => [] },
})

import { useRouter } from 'vue-router'

const emit = defineEmits(['plan'])
const router = useRouter()

function goDetails() {
  router.push({ name: 'destinationDetails', params: { id: props.destination.id } })
}

const hasMatch = computed(() => {
  try {
    return (props.matchTags || []).some((t) => (props.destination.tags || []).includes(t))
  } catch (e) {
    return false
  }
})

const formattedCost = computed(() => {
  if (props.destination.price_range_xaf) {
    return `${props.destination.price_range_xaf} XAF`
  }
  const v = props.destination.avg_cost_per_day
  if (typeof v === 'number') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v)
  }
  return ''
})
</script>

<template>
  <article
    class="group relative flex flex-col overflow-visible rounded-3xl border border-border-light bg-white shadow-md shadow-lavender/10 transition duration-200 hover:-translate-y-1 hover:shadow-lg hover:shadow-sage/10"
  >
    <!-- Main face -->
    <div class="p-6">
      <div class="flex items-start justify-between gap-2">
        <div>
          <h3 class="font-display text-2xl font-semibold leading-tight text-deep-blue">
            {{ destination.name }}
          </h3>
          <p class="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {{ destination.country }}
          </p>
        </div>
        <span
          v-if="hasMatch"
          class="stamp shrink-0 rounded-full px-3 py-1 text-[10px] font-semibold uppercase tracking-wider"
        >
          Match
        </span>
      </div>

      <p class="mt-3 text-sm leading-relaxed text-text-secondary">
        {{ destination.description }}
      </p>

      <div class="mt-4 flex flex-wrap gap-2">
        <span
          v-for="t in destination.tags"
          :key="t"
          class="rounded-full px-3 py-1 text-xs font-medium capitalize"
          :class="
            matchTags.includes(t)
              ? 'bg-sage/15 text-sage ring-1 ring-sage/30'
              : 'bg-lavender-light text-deep-blue'
          "
        >
          {{ t }}
        </span>
      </div>
    </div>

    <!-- Perforated stub: cost / climate / season -->
    <div class="perforated mx-6 flex items-center justify-between py-4 text-xs">
      <div class="font-mono">
        <span class="text-base font-semibold text-deep-blue">{{ formattedCost }}</span>
        <span class="text-text-secondary">/day</span>
      </div>
      <div class="text-right text-text-secondary">
        <div class="capitalize">{{ destination.climate }}</div>
        <div>{{ destination.best_season }}</div>
      </div>
    </div>

    <div class="px-6 pb-6">
      <div class="flex gap-3">
        <button
          type="button"
          class="flex-1 rounded-xl bg-deep-blue py-2.5 text-sm font-medium text-white transition group-hover:bg-sage"
          @click="emit('plan', destination)"
        >
          Plan a trip
        </button>
        <button
          type="button"
          class="rounded-xl border border-border-light bg-white/80 px-4 py-2 text-sm font-medium text-deep-blue hover:bg-sage/10"
          @click="goDetails"
        >
          Details
        </button>
      </div>
    </div>
  </article>
</template>
