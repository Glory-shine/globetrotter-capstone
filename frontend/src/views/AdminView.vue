<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import backgroundDestination from '../assets/images/backgrounds/background_destination.jpg'
import { getDestinationStats, createDestination } from '../api/destinations'
import { getUserStats, getItineraryStats } from '../api/admin'
import { toastStore } from '../stores/toast'
import { CATEGORY_EMOJIS, COMMUNES } from '../config'

const loading = ref(true)
const destStats = ref(null)
const userStats = ref(null)
const itineraryStats = ref(null)

const activeTab = ref('stats')
const submitting = ref(false)
const formError = ref('')

const categoryOptions = Object.keys(CATEGORY_EMOJIS).filter((k) => k !== 'all')

const form = reactive({
  name: '',
  country: COMMUNES[0],
  category: categoryOptions[0],
  tags: '',
  avg_cost_per_day: 0,
  description: '',
  anecdote: '',
  best_season: "Toute l'année",
  latitude: 5.4778,
  longitude: 10.4176,
  rating: 4.0,
  price_range_xaf: '',
  media_main: '',
})

async function loadStats() {
  loading.value = true
  try {
    const [d, u, i] = await Promise.all([getDestinationStats(), getUserStats(), getItineraryStats()])
    destStats.value = d
    userStats.value = u
    itineraryStats.value = i
  } catch {
    // interceptor already surfaced a toast
  } finally {
    loading.value = false
  }
}

const categoryEntries = computed(() =>
  Object.entries(destStats.value?.destinations_by_category || {}).sort((a, b) => b[1] - a[1]),
)
const communeEntries = computed(() => Object.entries(destStats.value?.destinations_by_commune || {}))
const maxCategoryCount = computed(() => Math.max(1, ...categoryEntries.value.map(([, n]) => n)))

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatDateTime(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function resetForm() {
  form.name = ''
  form.country = COMMUNES[0]
  form.category = categoryOptions[0]
  form.tags = ''
  form.avg_cost_per_day = 0
  form.description = ''
  form.anecdote = ''
  form.best_season = "Toute l'année"
  form.latitude = 5.4778
  form.longitude = 10.4176
  form.rating = 4.0
  form.price_range_xaf = ''
  form.media_main = ''
}

async function submitDestination() {
  formError.value = ''
  if (!form.name.trim() || !form.description.trim()) {
    formError.value = 'Le nom et la description sont obligatoires.'
    return
  }
  submitting.value = true
  try {
    await createDestination({
      name: form.name.trim(),
      country: form.country,
      category: form.category,
      tags: form.tags.split(',').map((t) => t.trim()).filter(Boolean),
      avg_cost_per_day: Number(form.avg_cost_per_day) || 0,
      description: form.description.trim(),
      anecdote: form.anecdote.trim(),
      best_season: form.best_season.trim() || "Toute l'année",
      latitude: Number(form.latitude),
      longitude: Number(form.longitude),
      rating: Number(form.rating) || 4,
      price_range_xaf: form.price_range_xaf.trim(),
      media_main: form.media_main.trim() || null,
      activities: [],
    })
    toastStore.success(`« ${form.name} » a été ajouté au catalogue.`)
    resetForm()
    loadStats()
    activeTab.value = 'stats'
  } catch {
    // interceptor already surfaced a toast
  } finally {
    submitting.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-10"
      :style="{ backgroundImage: `url(${backgroundDestination})` }"
    />
    <div class="relative mx-auto max-w-6xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Espace administrateur</p>
        <h1 class="mt-3 font-display text-4xl font-semibold text-deep-blue sm:text-5xl">Statistiques &amp; gestion</h1>
        <p class="mt-3 text-text-secondary">Vue d'ensemble du système et ajout manuel de lieux au catalogue.</p>
      </div>

      <div class="mt-8 flex gap-2 border-b border-border-light">
        <button
          type="button"
          class="rounded-t-xl px-4 py-2.5 text-sm font-medium transition"
          :class="activeTab === 'stats' ? 'border-b-2 border-sage text-sage' : 'text-text-secondary hover:text-sage'"
          @click="activeTab = 'stats'"
        >
          📊 Statistiques
        </button>
        <button
          type="button"
          class="rounded-t-xl px-4 py-2.5 text-sm font-medium transition"
          :class="activeTab === 'add' ? 'border-b-2 border-sage text-sage' : 'text-text-secondary hover:text-sage'"
          @click="activeTab = 'add'"
        >
          ➕ Ajouter un lieu
        </button>
      </div>

      <!-- Onglet Statistiques -->
      <div v-if="activeTab === 'stats'" class="mt-8">
        <div v-if="loading" class="animate-pulse text-sm text-text-secondary">Chargement des statistiques…</div>
        <template v-else>
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div class="rounded-2xl border border-border-light bg-white/80 p-5">
              <p class="font-mono text-[10px] uppercase tracking-[0.2em] text-sage">Utilisateurs</p>
              <p class="mt-2 font-display text-3xl font-semibold text-deep-blue">{{ userStats?.total_users ?? '—' }}</p>
              <p class="mt-1 text-xs text-text-secondary">
                dont {{ userStats?.users_by_role?.admin ?? 0 }} admin(s), {{ userStats?.users_with_preferences ?? 0 }} avec préférences
              </p>
            </div>
            <div class="rounded-2xl border border-border-light bg-white/80 p-5">
              <p class="font-mono text-[10px] uppercase tracking-[0.2em] text-sage">Lieux au catalogue</p>
              <p class="mt-2 font-display text-3xl font-semibold text-deep-blue">{{ destStats?.total_destinations ?? '—' }}</p>
              <p class="mt-1 text-xs text-text-secondary">
                {{ destStats?.free_destinations ?? 0 }} gratuits · {{ destStats?.paid_destinations ?? 0 }} payants
              </p>
            </div>
            <div class="rounded-2xl border border-border-light bg-white/80 p-5">
              <p class="font-mono text-[10px] uppercase tracking-[0.2em] text-sage">Favoris / Commentaires</p>
              <p class="mt-2 font-display text-3xl font-semibold text-deep-blue">
                {{ destStats?.total_favorites ?? '—' }} <span class="text-base text-text-light">/</span> {{ destStats?.total_comments ?? '—' }}
              </p>
              <p class="mt-1 text-xs text-text-secondary">♥ favoris / 💬 commentaires</p>
            </div>
            <div class="rounded-2xl border border-border-light bg-white/80 p-5">
              <p class="font-mono text-[10px] uppercase tracking-[0.2em] text-sage">Note moyenne</p>
              <p class="mt-2 font-display text-3xl font-semibold text-deep-blue">⭐ {{ destStats?.average_rating ?? '—' }}</p>
              <p class="mt-1 text-xs text-text-secondary">
                {{ destStats?.without_photo ?? 0 }} lieu(x) sans photo
              </p>
            </div>
            <div class="rounded-2xl border border-border-light bg-white/80 p-5">
              <p class="font-mono text-[10px] uppercase tracking-[0.2em] text-sage">Itinéraires planifiés</p>
              <p class="mt-2 font-display text-3xl font-semibold text-deep-blue">{{ itineraryStats?.total_itineraries ?? '—' }}</p>
              <p class="mt-1 text-xs text-text-secondary">
                moyenne {{ itineraryStats?.average_items_per_itinerary ?? '—' }} étape(s) / itinéraire
              </p>
            </div>
            <div class="rounded-2xl border border-border-light bg-white/80 p-5">
              <p class="font-mono text-[10px] uppercase tracking-[0.2em] text-sage">Voyageurs planificateurs</p>
              <p class="mt-2 font-display text-3xl font-semibold text-deep-blue">{{ itineraryStats?.unique_planners ?? '—' }}</p>
              <p class="mt-1 text-xs text-text-secondary">utilisateurs ayant créé ≥ 1 itinéraire</p>
            </div>
          </div>

          <div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <!-- Répartition par catégorie, avec mini barres -->
            <div class="rounded-2xl border border-border-light bg-white/80 p-6">
              <h3 class="font-display text-lg font-semibold text-deep-blue">Lieux par catégorie</h3>
              <div class="mt-4 space-y-2.5">
                <div v-for="[cat, n] in categoryEntries" :key="cat">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-text-secondary">{{ CATEGORY_EMOJIS[cat] || '📍' }} {{ cat }}</span>
                    <span class="font-semibold text-deep-blue">{{ n }}</span>
                  </div>
                  <div class="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-cream">
                    <div class="h-full rounded-full bg-sage" :style="{ width: `${(n / maxCategoryCount) * 100}%` }" />
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-2xl border border-border-light bg-white/80 p-6">
              <h3 class="font-display text-lg font-semibold text-deep-blue">Lieux par commune</h3>
              <div class="mt-4 space-y-2">
                <div v-for="[commune, n] in communeEntries" :key="commune" class="flex items-center justify-between text-sm">
                  <span class="text-text-secondary">{{ commune }}</span>
                  <span class="font-semibold text-deep-blue">{{ n }}</span>
                </div>
              </div>

              <h3 class="mt-6 font-display text-lg font-semibold text-deep-blue">Tags les plus utilisés</h3>
              <div v-if="!destStats?.top_tags?.length" class="mt-3 text-sm text-text-secondary">Aucun tag pour l'instant.</div>
              <div v-else class="mt-3 flex flex-wrap gap-2">
                <span
                  v-for="t in destStats.top_tags"
                  :key="t.tag"
                  class="rounded-full bg-lavender-light px-3 py-1 text-xs font-medium text-deep-blue"
                >
                  {{ t.tag }} · {{ t.count }}
                </span>
              </div>
            </div>

            <div class="rounded-2xl border border-border-light bg-white/80 p-6">
              <h3 class="font-display text-lg font-semibold text-deep-blue">Lieux les plus favorisés</h3>
              <div v-if="!destStats?.most_favorited?.length" class="mt-3 text-sm text-text-secondary">
                Aucun favori enregistré pour l'instant.
              </div>
              <ol v-else class="mt-4 space-y-2">
                <li
                  v-for="(item, idx) in destStats.most_favorited"
                  :key="item.name"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-text-secondary">{{ idx + 1 }}. {{ item.name }}</span>
                  <span class="font-semibold text-sage">♥ {{ item.favorites }}</span>
                </li>
              </ol>
            </div>

            <div class="rounded-2xl border border-border-light bg-white/80 p-6">
              <h3 class="font-display text-lg font-semibold text-deep-blue">Lieux les plus commentés</h3>
              <div v-if="!destStats?.most_commented?.length" class="mt-3 text-sm text-text-secondary">
                Aucun commentaire enregistré pour l'instant.
              </div>
              <ol v-else class="mt-4 space-y-2">
                <li
                  v-for="(item, idx) in destStats.most_commented"
                  :key="item.name"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-text-secondary">{{ idx + 1 }}. {{ item.name }}</span>
                  <span class="font-semibold text-sage">💬 {{ item.comments }}</span>
                </li>
              </ol>
            </div>

            <div class="rounded-2xl border border-border-light bg-white/80 p-6">
              <h3 class="font-display text-lg font-semibold text-deep-blue">Derniers utilisateurs inscrits</h3>
              <div v-if="!userStats?.recent_signups?.length" class="mt-3 text-sm text-text-secondary">Aucun utilisateur pour l'instant.</div>
              <ul v-else class="mt-4 space-y-2.5">
                <li v-for="u in userStats.recent_signups" :key="u.username" class="flex items-center justify-between text-sm">
                  <span class="text-text-secondary">
                    @{{ u.username }}
                    <span v-if="u.role === 'admin'" class="ml-1 rounded-full bg-sage/10 px-2 py-0.5 text-[10px] font-semibold uppercase text-sage">admin</span>
                  </span>
                  <span class="text-xs text-text-light">{{ formatDate(u.created_at) }}</span>
                </li>
              </ul>
            </div>

            <div class="rounded-2xl border border-border-light bg-white/80 p-6">
              <h3 class="font-display text-lg font-semibold text-deep-blue">Derniers itinéraires créés</h3>
              <div v-if="!itineraryStats?.recent_itineraries?.length" class="mt-3 text-sm text-text-secondary">
                Aucun itinéraire pour l'instant.
              </div>
              <ul v-else class="mt-4 space-y-2.5">
                <li v-for="(it, idx) in itineraryStats.recent_itineraries" :key="idx" class="flex items-center justify-between text-sm">
                  <span class="text-text-secondary">{{ it.title }} <span class="text-xs text-text-light">({{ it.items }} étape(s))</span></span>
                  <span class="text-xs text-text-light">{{ formatDateTime(it.created_at) }}</span>
                </li>
              </ul>
            </div>
          </div>
        </template>
      </div>

      <!-- Onglet Ajouter un lieu -->
      <div v-else class="mt-8 max-w-3xl rounded-3xl border border-border-light bg-white/85 p-7 shadow-lg">
        <p v-if="formError" class="mb-4 rounded-xl bg-sage/10 px-4 py-2 text-sm text-sage">{{ formError }}</p>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="sm:col-span-2">
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Nom du lieu *</label>
            <input v-model="form.name" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Commune</label>
            <select v-model="form.country" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20">
              <option v-for="c in COMMUNES" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Catégorie</label>
            <select v-model="form.category" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20">
              <option v-for="c in categoryOptions" :key="c" :value="c">{{ CATEGORY_EMOJIS[c] }} {{ c }}</option>
            </select>
          </div>

          <div class="sm:col-span-2">
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Description *</label>
            <textarea v-model="form.description" rows="3" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div class="sm:col-span-2">
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Anecdote « Le saviez-vous ? »</label>
            <textarea v-model="form.anecdote" rows="2" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Latitude *</label>
            <input v-model="form.latitude" type="number" step="0.0001" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Longitude *</label>
            <input v-model="form.longitude" type="number" step="0.0001" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Coût moyen (FCFA)</label>
            <input v-model="form.avg_cost_per_day" type="number" min="0" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Note (/5)</label>
            <input v-model="form.rating" type="number" min="0" max="5" step="0.1" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Fourchette de prix (texte)</label>
            <input v-model="form.price_range_xaf" placeholder="ex : 500 - 1 000 FCFA" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Meilleure saison</label>
            <input v-model="form.best_season" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div class="sm:col-span-2">
            <label class="mb-1.5 block text-sm font-medium text-text-primary">Tags (séparés par des virgules)</label>
            <input v-model="form.tags" placeholder="nature, panorama, famille" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>

          <div class="sm:col-span-2">
            <label class="mb-1.5 block text-sm font-medium text-text-primary">URL de la photo principale</label>
            <input v-model="form.media_main" placeholder="https://... ou /destinations/mon-lieu.jpg" class="w-full rounded-2xl border border-border-light bg-cream px-4 py-2.5 text-sm outline-none focus:border-sage focus:ring-2 focus:ring-sage/20" />
          </div>
        </div>

        <button
          type="button"
          class="mt-6 rounded-full bg-deep-blue px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-sage disabled:opacity-60"
          :disabled="submitting"
          @click="submitDestination"
        >
          {{ submitting ? 'Ajout en cours…' : 'Ajouter le lieu au catalogue' }}
        </button>
      </div>
    </div>
  </div>
</template>
