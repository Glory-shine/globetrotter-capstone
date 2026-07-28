<script setup>
import { useRouter } from 'vue-router'
import backgroundDestination from '../assets/images/backgrounds/background_destination.jpg'

const router = useRouter()

const regions = [
  { slug: 'centre', title: 'Centre', description: 'Yaoundé and the political heart of the country.', image: '/images/cards_regions images/Card_Centre_Cameroun.jpg' },
  { slug: 'littoral', title: 'Littoral', description: 'Douala, Limbe and the lively coast.', image: '/images/cards_regions images/Card_Littoral_Cameroun.jpg' },
  { slug: 'south', title: 'South', description: 'Coastal escapes and serene beaches.', image: '/images/cards_regions images/Card_Sud_Cameroun.jpg' },
  { slug: 'southwest', title: 'Southwest', description: 'Highland landscapes around Mount Cameroon.', image: '/images/cards_regions images/Card_south_west_Cameroun.jpg' },
  { slug: 'north', title: 'North', description: 'Savannahs, wildlife and wide-open horizons.', image: '/images/cards_regions images/Card_North_Cameroun.jpg' },
  { slug: 'far-north', title: 'Far North', description: 'Remote and authentic landscapes.', image: '/images/cards_regions images/Card_far_north_cameroun.jpg' },
  { slug: 'west', title: 'West', description: 'Traditional chiefdoms and cool highlands.', image: '/images/cards_regions images/Card_ouest_cameroun.jpg' },
  { slug: 'northwest', title: 'Northwest', description: 'Village trails and elevated scenery.', image: '/images/cards_regions images/Card_North_West_Cameroun.jpg' },
  { slug: 'east', title: 'East', description: 'Forest-rich landscapes and hidden routes.', image: '/images/cards_regions images/Card_Sud_Cameroun1.jpg' },
  { slug: 'adamawa', title: 'Adamawa', description: 'Plateaus and cultural routes in the interior.', image: '/images/cards_regions images/Card_adamawa_cameroun.jpg' },
]

function openRegion(regionSlug) {
  router.push({ name: 'regionDestinations', params: { regionSlug } })
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <div
      class="pointer-events-none absolute inset-0 bg-cover bg-center opacity-20"
      :style="{ backgroundImage: `url(${backgroundDestination})` }"
    />
    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <div class="max-w-2xl">
        <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Discover</p>
        <h1 class="mt-3 font-display text-5xl font-semibold text-deep-blue sm:text-6xl">
          Cameroon regions
        </h1>
        <p class="mt-3 text-lg leading-relaxed text-text-secondary">
          Explore the 10 major regions of Cameroon through curated destination cards and discover the places that make each one unique.
        </p>
      </div>

      <div class="mt-12 grid grid-cols-1 gap-8 md:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="region in regions"
          :key="region.slug"
          type="button"
          class="group overflow-hidden rounded-3xl border border-border-light bg-white/80 text-left shadow-lg shadow-lavender/10 transition duration-200 hover:-translate-y-1 hover:shadow-xl"
          @click="openRegion(region.slug)"
        >
          <div class="overflow-hidden">
            <img :src="region.image" :alt="region.title" class="h-44 w-full object-cover transition duration-300 group-hover:scale-105" />
          </div>
          <div class="p-6">
            <div class="flex items-center justify-between">
              <h2 class="font-display text-2xl font-semibold text-deep-blue">{{ region.title }}</h2>
              <span class="rounded-full bg-sage/10 px-3 py-1 text-xs font-medium uppercase tracking-wider text-sage">Open</span>
            </div>
            <p class="mt-3 text-sm leading-relaxed text-text-secondary">{{ region.description }}</p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
