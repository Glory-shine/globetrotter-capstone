import { reactive, readonly } from 'vue'

const state = reactive({
  toasts: [],
})

let nextId = 1

function push({ type = 'info', message, duration = 4500 }) {
  const id = nextId++
  state.toasts.push({ id, type, message })
  if (duration > 0) {
    setTimeout(() => dismiss(id), duration)
  }
  return id
}

function dismiss(id) {
  const index = state.toasts.findIndex((t) => t.id === id)
  if (index !== -1) state.toasts.splice(index, 1)
}

export const toastStore = {
  state: readonly(state),
  push,
  dismiss,
  success: (message) => push({ type: 'success', message }),
  error: (message) => push({ type: 'error', message }),
  info: (message) => push({ type: 'info', message }),
}
