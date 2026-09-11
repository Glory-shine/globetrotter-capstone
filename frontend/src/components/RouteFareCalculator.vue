<script setup>
import { computed, ref, watch } from 'vue'
import { getFareEstimate } from '../api/fare'

const props = defineProps({
  destinations: { type: Array, default: () => [] },
})

const originId = ref('')
const arrivalId = ref('')
const mode = ref('moto')
const result = ref(null)
const loading = ref(false)
const error = ref('')

const sorted = computed(() => [...(props.destinations || [])].sort((a, b) => a.name.localeCompare(b.name)))

const arrivalOptions = computed(() => sorted.value.filter((d) => d.id !== originId.value))
const originOptions = computed(() => sorted.value.filter((d) => d.id !== arrivalId.value))

function swap() {
  const tmp = originId.value
  originId.value = arrivalId.value
  arrivalId.value = tmp
}

async function estimate() {
  if (!originId.value || !arrivalId.value || originId.value === arrivalId.value) {
    result.value = null
    return
  }
  loading.value = true
  error.value = ''
  result.value = null
  try {
    result.value = await getFareEstimate({
      fromId: originId.value,
      toId: arrivalId.value,
      mode: mode.value,
    })
  } catch {
    error.value = "Impossible d'estimer le tarif pour le moment."
  } finally {
    loading.value = false
  }
}

watch([originId, arrivalId, mode], estimate)
</script>

<template>
  <div class="rounded-3xl border border-border-light bg-deep-blue p-6 text-cream shadow-lg sm:p-7">
    <div class="flex items-center gap-2">
      <span class="text-lg">🏍️</span>
      <h3 class="font-display text-lg font-semibold">Estimer un trajet</h3>
    </div>
    <p class="mt-1 text-xs text-cream/70">
      Choisissez un lieu de départ et d'arrivée parmi tous les lieux de Bafoussam pour estimer le tarif
      moto-taxi ou taxi, calculé sur la distance réelle entre les deux points.
    </p>

    <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto_1fr] sm:items-end">
      <div>
        <label class="mb-1.5 block text-xs font-medium uppercase tracking-wide text-cream/70">Départ</label>
        <select
          v-model="originId"
          class="w-full rounded-xl border border-cream/20 bg-cream/5 px-3 py-2.5 text-sm text-cream outline-none focus:border-sage focus:ring-2 focus:ring-sage/30"
        >
          <option value="" disabled class="text-text-primary">Choisir un lieu…</option>
          <option v-for="d in originOptions" :key="d.id" :value="d.id" class="text-text-primary">
            {{ d.name }}
          </option>
        </select>
      </div>

      <button
        type="button"
        class="mx-auto grid h-9 w-9 place-items-center rounded-full border border-cream/20 bg-cream/5 text-cream transition hover:border-sage hover:text-sage sm:mb-0.5"
        title="Inverser départ / arrivée"
        aria-label="Inverser départ et arrivée"
        @click="swap"
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
          <option v-for="d in arrivalOptions" :key="d.id" :value="d.id" class="text-text-primary">
            {{ d.name }}
          </option>
        </select>
      </div>
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

    <div v-if="originId && arrivalId && originId === arrivalId" class="mt-4 text-sm text-sage-light">
      Choisissez deux lieux différents pour estimer le trajet.
    </div>
    <div v-else-if="loading" class="mt-4 animate-pulse text-sm text-cream/60">Calcul de l'estimation…</div>
    <p v-else-if="error" class="mt-4 text-sm text-sage-light">{{ error }}</p>
    <div v-else-if="result" class="mt-4 rounded-xl border border-cream/15 bg-cream/5 p-4">
      <p class="text-xs uppercase tracking-[0.2em] text-cream/50">{{ result.from_name }} → {{ result.to_name }}</p>
      <div class="mt-1 flex items-baseline justify-between">
        <span class="font-display text-2xl font-semibold">{{ result.price_label }}</span>
        <span class="font-mono text-xs text-cream/60">{{ result.distance_km }} km · ~{{ result.duration_min }} min</span>
      </div>
      <p class="mt-2 text-xs leading-relaxed text-cream/60">{{ result.note }}</p>
    </div>
    <p v-else class="mt-4 text-sm text-cream/50">Choisissez un départ et une arrivée pour voir le tarif estimé.</p>
  </div>
</template>
