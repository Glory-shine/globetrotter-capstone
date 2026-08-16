<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { createItinerary } from '../api/itineraries'
import { toastStore } from '../stores/toast'

const props = defineProps({
  destinations: { type: Array, default: () => [] },
  initialDestinationId: { type: String, default: '' },
})
const emit = defineEmits(['created'])

const form = reactive({
  title: '',
  destination_id: props.initialDestinationId || '',
  start_date: '',
  end_date: '',
  items: [{ day: 1, activity: '' }],
})
const submitting = ref(false)
const dateError = ref('')

watch(
  () => props.initialDestinationId,
  (id) => {
    if (id) form.destination_id = id
  }
)

const tripLength = computed(() => {
  if (!form.start_date || !form.end_date) return null
  const start = new Date(form.start_date)
  const end = new Date(form.end_date)
  const days = Math.round((end - start) / 86400000) + 1
  return days > 0 ? days : null
})

function addItem() {
  const nextDay = form.items.length ? form.items[form.items.length - 1].day + 1 : 1
  form.items.push({ day: nextDay, activity: '' })
}

function removeItem(index) {
  form.items.splice(index, 1)
}

async function handleSubmit() {
  dateError.value = ''
  if (!form.start_date || !form.end_date) return
  if (new Date(form.end_date) < new Date(form.start_date)) {
    dateError.value = 'End date must be on or after the start date.'
    return
  }

  submitting.value = true
  try {
    const payload = {
      title: form.title.trim(),
      destination_id: form.destination_id,
      start_date: form.start_date,
      end_date: form.end_date,
      items: form.items
        .filter((i) => i.activity.trim())
        .map((i) => ({ day: Number(i.day), activity: i.activity.trim() })),
    }
    const created = await createItinerary(payload)
    toastStore.success(`“${created.title}” is booked into your itineraries.`)
    emit('created', created)

    form.title = ''
    form.destination_id = ''
    form.start_date = ''
    form.end_date = ''
    form.items = [{ day: 1, activity: '' }]
  } catch {
    // interceptor already surfaced a toast (404 unknown destination, 400 day overflow, etc.)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form
    class="overflow-hidden rounded-2xl border border-ink/10 bg-ink text-paper shadow-lg shadow-ink/10"
    @submit.prevent="handleSubmit"
  >
    <div class="p-6">
      <p class="font-mono text-xs uppercase tracking-[0.3em] text-gold">Nouvel itinéraire</p>
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div class="sm:col-span-2">
          <label for="it-title" class="mb-1.5 block text-sm font-medium text-paper/80">Titre de la visite</label>
          <input
            id="it-title"
            v-model="form.title"
            required
            type="text"
            placeholder="Journée culturelle en famille"
            class="w-full rounded-xl border border-paper/20 bg-paper/5 px-4 py-2.5 text-sm text-paper outline-none placeholder:text-paper/40 focus:border-coral focus:ring-2 focus:ring-coral/30"
          />
        </div>

        <div class="sm:col-span-2">
          <label for="it-destination" class="mb-1.5 block text-sm font-medium text-paper/80">Lieu</label>
          <select
            id="it-destination"
            v-model="form.destination_id"
            required
            class="w-full rounded-xl border border-paper/20 bg-paper/5 px-4 py-2.5 text-sm text-paper outline-none focus:border-coral focus:ring-2 focus:ring-coral/30"
          >
            <option value="" disabled class="text-ink">Choisir un lieu…</option>
            <option v-for="d in destinations" :key="d.id" :value="d.id" class="text-ink">
              {{ d.name }}, {{ d.country }}
            </option>
          </select>
        </div>

        <div>
          <label for="it-start" class="mb-1.5 block text-sm font-medium text-paper/80">Départ</label>
          <input
            id="it-start"
            v-model="form.start_date"
            required
            type="date"
            class="w-full rounded-xl border border-paper/20 bg-paper/5 px-4 py-2.5 text-sm text-paper outline-none focus:border-coral focus:ring-2 focus:ring-coral/30"
          />
        </div>
        <div>
          <label for="it-end" class="mb-1.5 block text-sm font-medium text-paper/80">Retour</label>
          <input
            id="it-end"
            v-model="form.end_date"
            required
            type="date"
            class="w-full rounded-xl border border-paper/20 bg-paper/5 px-4 py-2.5 text-sm text-paper outline-none focus:border-coral focus:ring-2 focus:ring-coral/30"
          />
        </div>
      </div>
      <p v-if="dateError" class="mt-2 text-xs text-coral">{{ dateError }}</p>
      <p v-else-if="tripLength" class="mt-2 font-mono text-xs text-paper/50">{{ tripLength }} jour(s) de visite</p>
    </div>

    <!-- Perforated tear between ticket header and day-by-day stub -->
    <div class="perforated mx-6" />

    <div class="space-y-3 p-6">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-paper/80">Programme jour par jour (optionnel)</span>
        <button
          type="button"
          class="text-xs font-medium text-coral hover:text-coral-dark"
          @click="addItem"
        >
          + Ajouter un jour
        </button>
      </div>

      <div
        v-for="(item, idx) in form.items"
        :key="idx"
        class="flex items-center gap-2 rounded-xl border border-paper/10 bg-paper/5 p-2"
      >
        <span class="font-mono text-xs text-gold">Jour</span>
        <input
          v-model.number="item.day"
          type="number"
          min="1"
          class="w-14 rounded-lg border border-paper/20 bg-transparent px-2 py-1.5 text-center text-sm text-paper outline-none focus:border-coral"
        />
        <input
          v-model="item.activity"
          type="text"
          placeholder="Quelle activité ?"
          class="flex-1 rounded-lg border border-paper/20 bg-transparent px-3 py-1.5 text-sm text-paper outline-none placeholder:text-paper/40 focus:border-coral"
        />
        <button
          v-if="form.items.length > 1"
          type="button"
          aria-label="Supprimer ce jour"
          class="text-paper/40 hover:text-coral"
          @click="removeItem(idx)"
        >
          ✕
        </button>
      </div>

      <button
        type="submit"
        :disabled="submitting"
        class="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-coral py-3 text-sm font-semibold text-paper transition hover:bg-coral-dark disabled:cursor-not-allowed disabled:opacity-60"
      >
        {{ submitting ? 'Enregistrement…' : "Créer l'itinéraire" }}
      </button>
    </div>
  </form>
</template>
