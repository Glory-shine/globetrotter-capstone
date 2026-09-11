import { reactive, readonly } from 'vue'

const state = reactive({
  byId: {},
})

function cache(destinations = []) {
  for (const dest of destinations) {
    state.byId[dest.id] = dest
  }
}

function get(id) {
  return state.byId[id] || null
}

export const destinationsCache = {
  state: readonly(state),
  cache,
  get,
}
