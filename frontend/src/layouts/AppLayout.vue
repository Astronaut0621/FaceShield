<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand-block" to="/">
        <svg class="brand-icon" viewBox="0 0 32 32" aria-hidden="true">
          <path
            d="M16 4L4 26h24L16 4zm0 6.5l6.8 13.5H9.2L16 10.5z"
            fill="currentColor"
          />
        </svg>
        <div>
          <h1>{{ appConfig.name }}</h1>
          <p>频域 · 空域融合检测</p>
        </div>
      </RouterLink>

      <nav>
        <RouterLink
          v-for="item in navigationItems"
          :key="item.name"
          :to="{ name: item.name }"
          :class="{ active: route.name === item.name }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </nav>

      <div v-if="authStore.isAuthenticated" class="session-box">
        <span class="user-name">{{ authStore.user?.display_name || authStore.user?.username }}</span>
        <button @click="signOut">退出登录</button>
      </div>
    </aside>
    <main>
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { appConfig } from '@/config/app.config'
import { navigationItems } from '@/constants/routes'
import { logout } from '@/features/auth/services/auth.service'
import { authStore } from '@/stores/auth.store'

const route = useRoute()

async function signOut() {
  try {
    await logout()
  } finally {
    authStore.clearSession()
    window.location.href = '/login'
  }
}
</script>

<style scoped>
.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
  text-decoration: none;
  color: inherit;
  border-radius: 10px;
  padding: 6px;
  margin-left: -6px;
  transition: background 0.15s;
}

.brand-block:hover {
  background: rgba(255, 255, 255, 0.06);
}

.brand-icon {
  width: 28px;
  height: 28px;
  color: #4ade80;
  flex-shrink: 0;
}

.brand-block h1 {
  margin: 0;
  font-size: 20px;
  letter-spacing: 0.02em;
  color: #fff;
}

.brand-block p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.sidebar nav a {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar nav a.active {
  background: rgba(22, 101, 52, 0.35);
  color: #fff;
  font-weight: 600;
}

.nav-icon {
  width: 20px;
  text-align: center;
  font-size: 15px;
}

.user-name {
  font-weight: 600;
  color: #e2e8f0;
}
</style>
