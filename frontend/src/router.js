import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from './stores/auth'

const routes = [
  { path: '/', redirect: '/destinations' },
  {
    path: '/login',
    name: 'login',
    component: () => import('./views/LoginView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('./views/RegisterView.vue'),
    meta: { guestOnly: true },
  },
  {
    path: '/region',
    name: 'region',
    component: () => import('./views/RegionView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/carte',
    name: 'map',
    component: () => import('./views/MapView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/destinations',
    name: 'destinations',
    component: () => import('./views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/destinations/:id',
    name: 'destinationDetails',
    component: () => import('./views/DestinationDetailsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('./views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('./views/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recommendations',
    name: 'recommendations',
    component: () => import('./views/RecommendationsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/itineraries',
    name: 'itineraries',
    component: () => import('./views/ItinerariesView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('./views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/destinations' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// Route guard: keeps unauthenticated users out of protected pages, and
// signed-in users out of the auth pages.
router.beforeEach((to) => {
  const authed = authStore.isAuthenticated()

  if (to.meta.requiresAuth && !authed) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !authStore.isAdmin()) {
    return { name: 'destinations' }
  }
  if (to.meta.guestOnly && authed) {
    return { name: 'destinations' }
  }
  return true
})

export default router
