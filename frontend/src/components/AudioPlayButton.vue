<script setup>
import { onBeforeUnmount, ref } from 'vue'

const props = defineProps({
  text: { type: String, required: true },
  label: { type: String, default: 'Écouter la description' },
})

const speaking = ref(false)
const supported = typeof window !== 'undefined' && 'speechSynthesis' in window

function speak() {
  if (!supported) return
  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(props.text)
  utterance.lang = 'fr-FR'
  utterance.rate = 0.98
  utterance.onend = () => (speaking.value = false)
  utterance.onerror = () => (speaking.value = false)

  speaking.value = true
  window.speechSynthesis.speak(utterance)
}

function stop() {
  if (!supported) return
  window.speechSynthesis.cancel()
  speaking.value = false
}

function toggle() {
  if (speaking.value) stop()
  else speak()
}

onBeforeUnmount(() => {
  if (supported) window.speechSynthesis.cancel()
})
</script>

<template>
  <button
    v-if="supported"
    type="button"
    class="inline-flex items-center gap-2 rounded-full border border-border-light bg-white px-4 py-2 text-sm font-medium text-deep-blue transition hover:border-sage hover:text-sage"
    @click="toggle"
  >
    <span v-if="speaking" class="flex gap-0.5">
      <span class="h-3 w-0.5 animate-pulse bg-sage" />
      <span class="h-3 w-0.5 animate-pulse bg-sage" style="animation-delay: 0.15s" />
      <span class="h-3 w-0.5 animate-pulse bg-sage" style="animation-delay: 0.3s" />
    </span>
    <span v-else>🔊</span>
    {{ speaking ? 'Arrêter la lecture' : label }}
  </button>
</template>
