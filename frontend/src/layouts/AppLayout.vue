<template>
  <div class="app-shell">
    <aside class="sidebar">
      <RouterLink class="brand-block" to="/">
        <span class="brand-mark" aria-hidden="true">F</span>
        <div>
          <h1>{{ appConfig.name }}</h1>
          <p>频域与空域融合检测</p>
        </div>
      </RouterLink>

      <nav aria-label="主导航">
        <RouterLink
          v-for="item in navigationItems"
          :key="item.name"
          :to="{ name: item.name }"
          :class="{ active: route.name === item.name }"
        >
          <span class="nav-icon" aria-hidden="true">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div v-if="authStore.isAuthenticated" class="session-box">
        <span class="session-label">当前账号</span>
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
  border-radius: 14px;
  padding: 8px;
  margin-left: -4px;
  transition: background 0.16s ease;
}

.brand-block:hover {
  background: rgba(255, 255, 255, 0.07);
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #5eeaa2, #087443);
  color: #062117;
  font-weight: 900;
  box-shadow: 0 12px 28px rgba(8, 116, 67, 0.28);
  flex-shrink: 0;
}

.brand-block h1 {
  margin: 0;
  font-size: 20px;
  letter-spacing: 0.01em;
  color: #fff;
}

.brand-block p {
  margin: 3px 0 0;
  color: rgba(231, 241, 236, 0.62);
  font-size: 12px;
}

.sidebar nav a {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 650;
}

.nav-icon {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.07);
  color: rgba(231, 241, 236, 0.82);
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
}

.sidebar nav a.active .nav-icon {
  background: rgba(94, 234, 162, 0.18);
  color: #5eeaa2;
}

.session-label {
  color: rgba(231, 241, 236, 0.52);
  font-size: 12px;
}

.user-name {
  font-weight: 750;
  color: #e7f1ec;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 900px) {
  .brand-block {
    margin-bottom: 14px;
  }

  .session-box {
    margin-top: 14px;
  }
}
</style>
