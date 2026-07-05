import { createRouter, createWebHistory } from 'vue-router'
import { routeNames } from '../constants/routes'
import { authStore } from '../stores/auth.store'
import LoginView from '../views/LoginView.vue'
import UploadView from '../views/UploadView.vue'
import HistoryView from '../views/HistoryView.vue'
import ResultView from '../views/ResultView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: routeNames.login, component: LoginView, meta: { public: true } },
    { path: '/', name: routeNames.detection, component: UploadView },
    { path: '/result', name: routeNames.result, component: ResultView },
    { path: '/history', name: routeNames.history, component: HistoryView }
  ]
})

router.beforeEach(to => {
  if (!to.meta.public && !authStore.isAuthenticated) {
    return { name: routeNames.login }
  }
  if (to.name === routeNames.login && authStore.isAuthenticated) {
    return { name: routeNames.detection }
  }
  return true
})

export default router
