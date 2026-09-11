<script setup>
import { toastStore } from '../stores/toast'

const styles = {
  error: 'border-coral/40 bg-ink text-paper',
  success: 'border-teal/40 bg-ink text-paper',
  info: 'border-gold/40 bg-ink text-paper',
}

const dots = {
  error: 'bg-coral',
  success: 'bg-teal',
  info: 'bg-gold',
}
</script>

<template>
  <div
    class="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex flex-col items-center gap-2 px-4 sm:items-end sm:right-4 sm:left-auto"
  >
    <transition-group name="toast">
      <div
        v-for="toast in toastStore.state.toasts"
        :key="toast.id"
        class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl border px-4 py-3 shadow-lg shadow-ink/20"
        :class="styles[toast.type] || styles.info"
        role="status"
      >
        <span class="mt-1.5 h-2 w-2 shrink-0 rounded-full" :class="dots[toast.type] || dots.info" />
        <p class="flex-1 text-sm leading-snug">{{ toast.message }}</p>
        <button
          type="button"
          class="text-paper/60 transition hover:text-paper"
          aria-label="Dismiss"
          @click="toastStore.dismiss(toast.id)"
        >
          ✕
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(8px);
}
</style>
