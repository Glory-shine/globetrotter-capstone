<script setup>
import { computed, ref } from 'vue'

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

const props = defineProps({
  destination: { type: Object, required: true },
  matchTags: { type: Array, default: () => [] },
})

import { useRouter } from 'vue-router'

const emit = defineEmits(['plan'])
const router = useRouter()
const liked = ref(Boolean(props.destination?.liked))
const likes = ref(Number(props.destination?.likes ?? 0))

function toggleLike() {
  liked.value = !liked.value
  likes.value = liked.value ? likes.value + 1 : Math.max(0, likes.value - 1)
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

const imageSrc = computed(() => {
  if (props.destination?.media?.main) return props.destination.media.main
  if (props.destination?.name && imageByName[props.destination.name]) return imageByName[props.destination.name]
  return null
})
</script>

<template>
  <article
    class="group relative flex flex-col overflow-visible rounded-3xl border border-border-light bg-white shadow-md shadow-lavender/10 transition duration-200 hover:-translate-y-1 hover:shadow-lg hover:shadow-sage/10"
  >
    <!-- Main face -->
    <div class="p-6">
      <div v-if="imageSrc" class="mb-4 overflow-hidden rounded-2xl border border-border-light bg-cream">
        <img
          :src="imageSrc"
          :alt="`${destination.name} image`"
          class="h-40 w-full object-cover transition duration-300 group-hover:scale-105"
        />
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
            class="rounded-full border border-border-light px-2.5 py-1.5 text-sm transition"
            :class="liked ? 'bg-sage/10 text-sage' : 'bg-white text-text-secondary hover:bg-sage/10'"
            @click="toggleLike"
            aria-label="Like destination"
          >
            ♥
          </button>
          <span class="text-sm font-medium text-text-secondary">{{ likes }}</span>
          <span
            v-if="hasMatch"
            class="stamp shrink-0 rounded-full px-3 py-1 text-[10px] font-semibold uppercase tracking-wider"
          >
            Match
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

    <div class="perforated mx-6 py-4 text-xs text-text-secondary">
      <div class="capitalize">{{ destination.climate }}</div>
      <div>{{ destination.best_season }}</div>
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
