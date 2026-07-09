import { createRouter, createWebHistory } from 'vue-router'
import { routeNames } from '@/constants/routes'
import { authStore } from '@/stores/auth.store'
import LoginView from '@/views/auth/LoginView.vue'
import HomeView from '@/views/home/HomeView.vue'
import DetectiveView from '@/views/detective/DetectiveView.vue'
import HistoryView from '@/views/history/HistoryView.vue'
import HistoryDetailView from '@/views/history/HistoryDetailView.vue'
import ResultView from '@/views/result/ResultView.vue'
import AssetCenterView from '@/views/assets/AssetCenterView.vue'
import SettingsView from '@/views/settings/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: routeNames.home, component: HomeView, meta: { public: true, standalone: true } },
    { path: '/login', name: routeNames.login, component: LoginView, meta: { public: true, standalone: true } },
    { path: '/detective', name: routeNames.detective, component: DetectiveView },
    { path: '/assets', name: routeNames.assets, component: AssetCenterView },
    { path: '/detection', redirect: '/detective' },
    { path: '/result/:id', name: routeNames.result, component: ResultView },
    { path: '/history', name: routeNames.history, component: HistoryView },
    { path: '/history/:id', name: routeNames.historyDetail, component: HistoryDetailView },
    { path: '/settings', name: routeNames.settings, component: SettingsView }
  ]
})

router.beforeEach(to => {
  if (!to.meta.public && !authStore.isAuthenticated) {
    return { name: routeNames.login, query: { redirect: to.fullPath } }
  }
  if (to.name === routeNames.login && authStore.isAuthenticated) {
    return { name: routeNames.detective }
  }
  return true
})

export default router
