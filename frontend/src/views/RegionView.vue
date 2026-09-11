<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

// Photo aérienne réelle de Bafoussam, hébergée sur Wikimedia Commons (même
// approche de sourcing que le catalogue de destinations — voir
// services/recommendation-service/app/seed_data.py).
const heroImage =
  'https://commons.wikimedia.org/wiki/Special:FilePath/Vue%20a%C3%A9rienne%20de%20la%20ville%20de%20Bafoussam%20(9).jpg?width=1600'

const keyFacts = [
  { label: 'Région', value: 'Ouest-Cameroun', icon: '📍' },
  { label: 'Département', value: 'Mifi (chef-lieu)', icon: '🏛️' },
  { label: 'Population', value: '≈ 380 000 hab. (ville)', icon: '👥' },
  { label: 'Altitude', value: '≈ 1 420 - 1 520 m', icon: '⛰️' },
  { label: 'Langues', value: 'Français, Bamiléké (Yemba/Fe\u02BCefe\u02BCe)', icon: '🗣️' },
  { label: 'Distance de Yaoundé', value: '≈ 294 km au nord-ouest', icon: '🚌' },
]

const funFacts = [
  {
    title: 'Une ville aussi jeune que millénaire',
    text: "Le peuplement de Bafoussam remonte au 14ᵉ siècle, mais la ville n'a été érigée en Communauté Urbaine — regroupant les communes de Bafoussam I, II (Baleng) et III (Bamougoum) — qu'en 2008.",
  },
  {
    title: "Fussep, son nom en langue locale",
    text: "En bamiléké, Bafoussam se dit « Fussep ». C'est à la fois le nom de la ville et celui du peuple qui l'habite depuis des générations.",
  },
  {
    title: "3ᵉ ville économique du pays",
    text: "Après Yaoundé et Douala, Bafoussam est considérée comme la troisième ville la plus importante du Cameroun sur le plan financier — cœur battant du commerce dans les montagnes Bamboutos.",
  },
  {
    title: 'Un climat de plateau',
    text: "Perchée à plus de 1 400 m d'altitude sur le plateau bamiléké, Bafoussam bénéficie d'un climat tropical de savane bien plus frais que les villes côtières comme Douala.",
  },
  {
    title: 'Café, marchés et artisanat',
    text: "Historiquement bâtie sur la culture du café arabica, la ville reste aujourd'hui animée par ses grands marchés (Marché A et B) et son artisanat bamiléké réputé dans tout le pays.",
  },
]
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-gradient-to-br from-cream via-lavender-light to-cream">
    <!-- Hero -->
    <section class="relative">
      <div class="relative h-[46vh] min-h-[320px] w-full overflow-hidden sm:h-[52vh]">
        <img :src="heroImage" alt="Vue aérienne de la ville de Bafoussam" class="h-full w-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-t from-deep-blue/90 via-deep-blue/40 to-deep-blue/10" />
        <div class="absolute inset-x-0 bottom-0 mx-auto max-w-7xl px-6 pb-10 sm:px-8">
          <p class="font-mono text-xs uppercase tracking-[0.35em] text-lavender-light">Découvrir la région</p>
          <h1 class="mt-3 font-display text-4xl font-semibold text-white sm:text-6xl">
            L'Ouest-Cameroun, terre des Bamiléké
          </h1>
          <p class="mt-3 max-w-2xl text-sm leading-relaxed text-white/85 sm:text-base">
            Capitale régionale nichée dans les montagnes Bamboutos, Bafoussam est le point de départ
            idéal pour explorer chefferies, marchés et sites naturels de l'Ouest-Cameroun.
          </p>
        </div>
      </div>
      <div class="bamileke-band" />
    </section>

    <div class="relative mx-auto max-w-7xl px-6 py-12 sm:px-8">
      <!-- Fiche d'identité -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <div
          v-for="fact in keyFacts"
          :key="fact.label"
          class="rounded-2xl border border-border-light bg-white/80 p-4 text-center shadow-sm backdrop-blur"
        >
          <p class="text-2xl">{{ fact.icon }}</p>
          <p class="mt-2 font-mono text-[10px] uppercase tracking-[0.2em] text-sage">{{ fact.label }}</p>
          <p class="mt-1 text-sm font-semibold leading-snug text-deep-blue">{{ fact.value }}</p>
        </div>
      </div>

      <!-- Présentation -->
      <div class="mt-12 grid grid-cols-1 gap-10 lg:grid-cols-[1.4fr_1fr]">
        <div class="rounded-3xl border border-border-light bg-white/80 p-8 shadow-lg backdrop-blur-xl sm:p-10">
          <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Emplacement &amp; identité</p>
          <h2 class="mt-2 font-display text-3xl font-semibold text-deep-blue">Bafoussam, chef-lieu de l'Ouest</h2>
          <p class="mt-4 text-sm leading-relaxed text-text-secondary sm:text-base">
            Bafoussam est la capitale de la région de l'Ouest et du département de la Mifi, au Cameroun.
            Située sur le plateau bamiléké, dans les montagnes Bamboutos, à environ 1 420 mètres
            d'altitude, elle s'étend au pied de la colline de Banengo, à quelque 294 km au nord-ouest de
            Yaoundé, la capitale nationale.
          </p>
          <p class="mt-4 text-sm leading-relaxed text-text-secondary sm:text-base">
            Berceau du peuple bamiléké, la ville est aussi le foyer d'une langue et d'une culture riches,
            portées par ses chefferies traditionnelles, ses cérémonies rythmées au tam-tam et son
            artisanat (calebasses sculptées, tissus ndop, perles). Le français est la langue
            administrative, mais le bamiléké (dont les variantes Yemba et Fe'efe'e) reste la langue du
            quotidien pour une grande partie de la population.
          </p>
          <button
            type="button"
            class="mt-6 inline-flex items-center gap-2 rounded-full bg-deep-blue px-6 py-3 text-sm font-semibold text-white transition hover:bg-sage"
            @click="router.push({ name: 'destinations' })"
          >
            Explorer les lieux de Bafoussam
            <span aria-hidden="true">→</span>
          </button>
        </div>

        <div class="rounded-3xl border border-border-light bg-deep-blue p-8 text-cream shadow-lg sm:p-10">
          <p class="font-mono text-xs uppercase tracking-[0.3em] text-cream/60">En bref</p>
          <ul class="mt-4 space-y-4 text-sm leading-relaxed text-cream/85">
            <li class="flex gap-3">
              <span class="text-lg">👑</span>
              <span>Ville et village du peuple bamiléké, l'une des dix villes les plus peuplées du Cameroun.</span>
            </li>
            <li class="flex gap-3">
              <span class="text-lg">🌾</span>
              <span>Économie historiquement bâtie sur le café arabica, aujourd'hui portée par le commerce et l'agriculture vivrière.</span>
            </li>
            <li class="flex gap-3">
              <span class="text-lg">🏙️</span>
              <span>Statut de Communauté Urbaine depuis 2008, réunissant Bafoussam I, II (Baleng) et III (Bamougoum).</span>
            </li>
            <li class="flex gap-3">
              <span class="text-lg">✈️</span>
              <span>Reliée à Douala par l'aéroport de Bafoussam-Bamougoum (BFX) et desservie par la route nationale 4.</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Faits divers / le saviez-vous -->
      <div class="mt-14">
        <p class="font-mono text-xs uppercase tracking-[0.3em] text-sage">Le saviez-vous ?</p>
        <h2 class="mt-2 font-display text-3xl font-semibold text-deep-blue">Quelques faits sur Bafoussam</h2>

        <div class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div
            v-for="fact in funFacts"
            :key="fact.title"
            class="rounded-2xl border border-border-light bg-white/80 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-md"
          >
            <h3 class="font-display text-lg font-semibold text-deep-blue">{{ fact.title }}</h3>
            <p class="mt-2 text-sm leading-relaxed text-text-secondary">{{ fact.text }}</p>
          </div>
        </div>
      </div>

      <!-- CTA final -->
      <div class="mt-14 rounded-3xl border border-sage/30 bg-sage/10 p-8 text-center sm:p-12">
        <h2 class="font-display text-2xl font-semibold text-deep-blue sm:text-3xl">
          Prêt·e à découvrir Bafoussam de plus près ?
        </h2>
        <p class="mx-auto mt-3 max-w-xl text-sm text-text-secondary sm:text-base">
          Chefferies, musées, marchés, hôtels, restaurants et sites naturels réels vous attendent,
          avec la carte, les tarifs de transport et vos recommandations personnalisées.
        </p>
        <button
          type="button"
          class="mt-6 inline-flex items-center gap-2 rounded-full bg-deep-blue px-7 py-3 text-sm font-semibold text-white transition hover:bg-sage"
          @click="router.push({ name: 'destinations' })"
        >
          Explorer
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </div>
  </div>
</template>
