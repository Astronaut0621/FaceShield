<template>
  <div class="app-shell">
    <aside class="sidebar">
      <h1>{{ appConfig.name }}</h1>
      <nav>
        <RouterLink v-for="item in navigationItems" :key="item.name" :to="item.path">
          {{ item.label }}
        </RouterLink>
      </nav>
      <div v-if="authStore.isAuthenticated" class="session-box">
        <span>{{ authStore.user?.display_name || authStore.user?.username }}</span>
        <button @click="signOut">Logout</button>
      </div>
    </aside>
    <main>
      <slot />
    </main>
  </div>
</template>

<script setup>
import { appConfig } from '../config/app.config'
import { navigationItems } from '../constants/routes'
import { logout } from '../features/auth/services/auth.service'
import { authStore } from '../stores/auth.store'

async function signOut() {
  try {
    await logout()
  } finally {
    authStore.clearSession()
    window.location.href = '/login'
  }
}
</script>
