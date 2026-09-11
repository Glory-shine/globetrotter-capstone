<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toggleFavorite } from '../api/destinations'

const props = defineProps({
  destination: { type: Object, required: true },
  matchTags: { type: Array, default: () => [] },
})

const emit = defineEmits(['plan'])
const router = useRouter()
const favoriteBusy = ref(false)

async function toggleLike() {
  if (favoriteBusy.value) return
  favoriteBusy.value = true
  try {
    const updated = await toggleFavorite(props.destination.id)
    props.destination.is_favorite = updated.is_favorite
  } catch {
    // interceptor already surfaced a toast
  } finally {
    favoriteBusy.value = false
  }
}

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

const imageSrc = computed(() => props.destination?.media?.main || null)

const priceLabel = computed(() => {
  const d = props.destination
  if (d?.price_range_xaf) return d.price_range_xaf
  if (!d?.avg_cost_per_day) return 'Gratuit'
  return `${d.avg_cost_per_day.toLocaleString('fr-FR')} FCFA`
})
</script>

<template>
  <article
    class="group relative flex flex-col overflow-visible rounded-3xl border border-border-light bg-white shadow-md shadow-lavender/10 transition duration-200 hover:-translate-y-1 hover:shadow-lg hover:shadow-sage/10"
  >
    <div class="p-6">
      <div v-if="imageSrc" class="relative mb-4 overflow-hidden rounded-2xl border border-border-light bg-cream">
        <img
          :src="imageSrc"
          :alt="`Photo de ${destination.name}`"
          class="h-40 w-full object-cover transition duration-300 group-hover:scale-105"
        />
        <span
          class="absolute left-2 top-2 rounded-full bg-white/90 px-2.5 py-1 text-[11px] font-semibold text-deep-blue shadow"
        >
          {{ destination.category }}
        </span>
      </div>

      <div class="flex items-start justify-between gap-2">
        <div>
          <h3 class="font-display text-2xl font-semibold leading-tight text-deep-blue">
            {{ destination.name }}
          </h3>
          <p class="font-mono text-xs uppercase tracking-widest text-text-secondary">
            {{ destination.country }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="rounded-full border border-border-light px-2.5 py-1.5 text-sm transition disabled:opacity-60"
            :class="destination.is_favorite ? 'bg-sage/10 text-sage' : 'bg-white text-text-secondary hover:bg-sage/10'"
            :disabled="favoriteBusy"
            @click="toggleLike"
            :aria-label="destination.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'"
            :title="destination.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'"
          >
            {{ destination.is_favorite ? '♥' : '♡' }}
          </button>
          <span
            v-if="hasMatch"
            class="stamp shrink-0 rounded-full px-3 py-1 text-[10px] font-semibold uppercase tracking-wider"
          >
            Pour vous
          </span>
        </div>
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

    <div class="perforated mx-6 flex items-center justify-between py-4 text-xs text-text-secondary">
      <span class="flex items-center gap-1">⭐ {{ destination.rating?.toFixed(1) ?? '—' }}</span>
      <span
        class="font-mono font-semibold text-sage"
        title="Prix maximum indicatif — généralement négociable sur place"
        >{{ priceLabel }}</span
      >
    </div>

    <div class="px-6 pb-6">
      <div class="flex gap-3">
        <button
          type="button"
          class="flex-1 rounded-xl bg-deep-blue py-2.5 text-sm font-medium text-white transition group-hover:bg-sage"
          @click="emit('plan', destination)"
        >
          Planifier
        </button>
        <button
          type="button"
          class="rounded-xl border border-border-light bg-white/80 px-4 py-2 text-sm font-medium text-deep-blue hover:bg-sage/10"
          @click="goDetails"
        >
          Détails
        </button>
      </div>
    </div>
  </article>
</template>
