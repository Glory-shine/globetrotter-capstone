// jsdom doesn't implement the Clipboard API; ItineraryCard's "Share" action
// calls it, so stub it out for tests that don't explicitly mock it.
if (!navigator.clipboard) {
  Object.defineProperty(navigator, 'clipboard', {
    value: { writeText: () => Promise.resolve() },
    configurable: true,
  })
}
