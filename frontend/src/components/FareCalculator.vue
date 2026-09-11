<script setup>
import { computed, ref, watch } from 'vue'
import { getFareEstimate } from '../api/fare'

const props = defineProps({
  destination: { type: Object, required: true },
  allDestinations: { type: Array, default: () => [] },
})

const originId = ref('')
const mode = ref('moto')
const result = ref(null)
const loading = ref(false)
const error = ref('')

const originOptions = computed(() =>
  (props.allDestinations || []).filter((d) => d.id !== props.destination.id)
)

async function estimate() {
  if (!originId.value) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await getFareEstimate({
      fromId: originId.value,
      toId: props.destination.id,
      mode: mode.value,
    })
  } catch {
    error.value = "Impossible d'estimer le tarif pour le moment."
  } finally {
    loading.value = false
  }
}

watch([originId, mode], estimate)
</script>

<template>
  <div class="rounded-2xl border border-border-light bg-deep-blue p-5 text-cream shadow-lg">
    <div class="flex items-center gap-2">
      <span class="text-lg">🏍️</span>
      <h3 class="font-display text-lg font-semibold">Comment s'y rendre</h3>
    </div>
    <p class="mt-1 text-xs text-cream/70">
      Estimation du tarif moto-taxi ou taxi, calculée sur la distance réelle entre les deux lieux.
    </p>

    <div class="mt-4">
      <label class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-cream/70">
        Je pars de…
      </label>
      <select
        v-model="originId"
        class="w-full rounded-xl border border-cream/20 bg-cream/5 px-3 py-2.5 text-sm text-cream outline-none focus:border-sage focus:ring-2 focus:ring-sage/30"
      >
        <option value="" disabled class="text-text-primary">Choisir un lieu de départ…</option>
        <option v-for="d in originOptions" :key="d.id" :value="d.id" class="text-text-primary">
          {{ d.name }}
        </option>
      </select>
    </div>

    <div class="mt-4 flex gap-2">
      <button
        type="button"
        class="flex-1 rounded-xl border-2 px-4 py-2.5 text-sm font-medium transition"
        :class="mode === 'moto' ? 'border-sage bg-sage text-white' : 'border-cream/20 text-cream hover:border-sage'"
        @click="mode = 'moto'"
      >
        🏍️ Moto-taxi
      </button>
      <button
        type="button"
        class="flex-1 rounded-xl border-2 px-4 py-2.5 text-sm font-medium transition"
        :class="mode === 'taxi' ? 'border-sage bg-sage text-white' : 'border-cream/20 text-cream hover:border-sage'"
        @click="mode = 'taxi'"
      >
        🚕 Taxi
      </button>
    </div>

    <div v-if="loading" class="mt-4 animate-pulse text-sm text-cream/60">Calcul de l'estimation…</div>
    <p v-else-if="error" class="mt-4 text-sm text-sage-light">{{ error }}</p>
    <div v-else-if="result" class="mt-4 rounded-xl border border-cream/15 bg-cream/5 p-4">
      <div class="flex items-baseline justify-between">
        <span class="font-display text-2xl font-semibold">{{ result.price_label }}</span>
        <span class="font-mono text-xs text-cream/60">{{ result.distance_km }} km · ~{{ result.duration_min }} min</span>
      </div>
      <p class="mt-2 text-xs leading-relaxed text-cream/60">{{ result.note }}</p>
    </div>
    <p v-else class="mt-4 text-sm text-cream/50">Choisissez un point de départ pour voir le tarif estimé.</p>
  </div>
</template>
