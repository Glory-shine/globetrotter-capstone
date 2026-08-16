<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { searchDestinations } from '../api/destinations'
import { destinationsCache } from '../stores/destinationsCache'
import { PREFERENCE_TAGS } from '../config'

const router = useRouter()

const budget = ref('')
const selectedTags = ref([])
const loading = ref(false)
const asked = ref(false)
const suggestions = ref([])

function toggleTag(tag) {
  const idx = selectedTags.value.indexOf(tag)
  if (idx === -1) selectedTags.value.push(tag)
  else selectedTags.value.splice(idx, 1)
}

function formatFcfa(n) {
  return n > 0 ? `${Number(n).toLocaleString('fr-FR')} FCFA` : 'Gratuit'
}

const assistantMessage = ref(
  "Bonjour ! Dites-moi votre budget et ce qui vous intéresse, je vous propose des lieux à Bafoussam qui correspondent."
)

async function ask() {
  loading.value = true
  asked.value = true
  try {
    // The backend filters by a single tag at a time — fetch by budget
    // (and the first chosen interest, if any), then refine client-side
    // against every interest selected so the assistant still feels smart
    // about combining several at once.
    const primaryTag = selectedTags.value[0] || undefined
    const data = await searchDestinations({
      max_cost: budget.value || undefined,
      tag: primaryTag,
    })
    destinationsCache.cache(data)

    let refined = data
    if (selectedTags.value.length > 1) {
      refined = data.filter((d) => selectedTags.value.every((t) => (d.tags || []).includes(t)))
      if (!refined.length) refined = data // fall back rather than showing nothing
    }

    suggestions.value = refined.slice(0, 4)

    if (!suggestions.value.length) {
      assistantMessage.value =
        "Je n'ai rien trouvé d'aussi précis — essayez d'augmenter un peu le budget ou de retirer un centre d'intérêt."
    } else if (budget.value) {
      assistantMessage.value = `Voici ${suggestions.value.length} lieu(x) à moins de ${formatFcfa(Number(budget.value))} qui devrai(en)t vous plaire :`
    } else {
      assistantMessage.value = `Voici ${suggestions.value.length} lieu(x) qui correspondent à vos envies :`
    }
  } catch {
    assistantMessage.value = "Je n'ai pas pu récupérer de suggestions pour le moment — réessayez dans un instant."
  } finally {
    loading.value = false
  }
}

function reset() {
  budget.value = ''
  selectedTags.value = []
  suggestions.value = []
  asked.value = false
  assistantMessage.value =
    "Bonjour ! Dites-moi votre budget et ce qui vous intéresse, je vous propose des lieux à Bafoussam qui correspondent."
}

function goToDestination(id) {
  router.push({ name: 'destinationDetails', params: { id } })
}
</script>

<template>
  <div class="rounded-3xl border border-border-light bg-deep-blue p-6 text-cream shadow-lg sm:p-8">
    <div class="flex items-start gap-3">
      <div class="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-sage text-lg">🧭</div>
      <div class="flex-1">
        <p class="font-mono text-[11px] uppercase tracking-[0.3em] text-cream/60">Assistant Bafoussam</p>
        <div class="mt-2 rounded-2xl rounded-tl-sm bg-cream/10 px-4 py-3 text-sm leading-relaxed">
          {{ assistantMessage }}
        </div>
      </div>
    </div>

    <div class="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-[auto_1fr] sm:items-center">
      <label for="assistant-budget" class="text-sm font-medium text-cream/80">Mon budget par lieu</label>
      <div class="flex items-center gap-2">
        <input
          id="assistant-budget"
          v-model="budget"
          type="number"
          min="0"
          placeholder="ex. 1500"
          class="w-32 rounded-xl border border-cream/20 bg-cream/5 px-3 py-2 text-sm text-cream outline-none focus:border-sage focus:ring-2 focus:ring-sage/30"
        />
        <span class="text-xs text-cream/60">FCFA</span>
      </div>
    </div>

    <div class="mt-4">
      <p class="text-sm font-medium text-cream/80">Ce qui m'intéresse (optionnel)</p>
      <div class="mt-2 flex flex-wrap gap-2">
        <button
          v-for="tag in PREFERENCE_TAGS"
          :key="tag"
          type="button"
          class="rounded-full px-3 py-1.5 text-xs font-medium capitalize transition"
          :class="selectedTags.includes(tag) ? 'bg-sage text-white' : 'bg-cream/10 text-cream/80 hover:bg-cream/20'"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>

    <div class="mt-5 flex gap-3">
      <button
        type="button"
        :disabled="loading"
        class="rounded-full bg-sage px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-sage-light disabled:cursor-not-allowed disabled:opacity-60"
        @click="ask"
      >
        {{ loading ? 'Recherche…' : 'Trouver des lieux pour moi' }}
      </button>
      <button
        v-if="asked"
        type="button"
        class="rounded-full border border-cream/20 px-5 py-2.5 text-sm font-medium text-cream/80 hover:border-cream/40"
        @click="reset"
      >
        Recommencer
      </button>
    </div>

    <div v-if="suggestions.length" class="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <button
        v-for="d in suggestions"
        :key="d.id"
        type="button"
        class="flex items-center gap-3 rounded-2xl border border-cream/15 bg-cream/5 p-3 text-left transition hover:border-sage hover:bg-cream/10"
        @click="goToDestination(d.id)"
      >
        <img
          v-if="d.media?.main"
          :src="d.media.main"
          :alt="d.name"
          class="h-14 w-14 shrink-0 rounded-xl object-cover"
        />
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold text-cream">{{ d.name }}</p>
          <p class="text-xs text-cream/60">{{ d.category }} · {{ formatFcfa(d.avg_cost_per_day) }}</p>
        </div>
      </button>
    </div>
  </div>
</template>
