<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand-block" to="/">
        <span class="brand-mark" aria-hidden="true">F</span>
        <div>
          <h1>{{ appConfig.name }}</h1>
          <p>频域与空域融合检测</p>
        </div>
      </RouterLink>

      <nav class="top-nav" aria-label="主导航">
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
    </header>
    <main class="app-main">
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
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: minmax(190px, auto) minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  min-height: 72px;
  padding: 12px 28px;
  background:
    linear-gradient(180deg, rgba(17, 24, 39, 0.98), rgba(30, 41, 59, 0.98)),
    #111827;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.14);
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  border-radius: 14px;
  padding: 8px;
  transition: background 0.16s ease;
  min-width: 0;
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
  background: linear-gradient(135deg, var(--accent-glow), var(--accent));
  color: #0f172a;
  font-weight: 900;
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.28);
  flex-shrink: 0;
}

.brand-block h1 {
  margin: 0;
  font-size: 20px;
  color: #fff;
}

.brand-block p {
  margin: 3px 0 0;
  color: rgba(226, 232, 240, 0.68);
  font-size: 12px;
}

.top-nav {
  display: flex;
  justify-content: center;
  gap: 8px;
  min-width: 0;
}

.top-nav a {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  color: rgba(231, 241, 236, 0.78);
  text-decoration: none;
  padding: 9px 12px;
  border-radius: 12px;
  font-weight: 650;
  transition:
    background 0.16s ease,
    color 0.16s ease,
    transform 0.16s ease;
}

.top-nav a:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.top-nav a.router-link-active,
.top-nav a.active {
  background: rgba(147, 197, 253, 0.16);
  color: #fff;
  box-shadow: inset 0 0 0 1px rgba(147, 197, 253, 0.2);
}

.nav-icon {
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border-radius: 9px;
  background: rgba(255, 255, 255, 0.07);
  color: rgba(226, 232, 240, 0.82);
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
}

.top-nav a.active .nav-icon {
  background: rgba(147, 197, 253, 0.18);
  color: var(--accent-glow);
}

.session-box {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  color: rgba(231, 241, 236, 0.78);
  font-size: 14px;
}

.session-label {
  color: rgba(226, 232, 240, 0.56);
  font-size: 12px;
  white-space: nowrap;
}

.user-name {
  max-width: 140px;
  font-weight: 750;
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-box button {
  min-height: 36px;
  padding: 0 12px;
  background: rgba(255, 255, 255, 0.1);
  white-space: nowrap;
}

.session-box button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.16);
  box-shadow: none;
}

@media (max-width: 980px) {
  .topbar {
    grid-template-columns: 1fr;
    align-items: stretch;
    gap: 10px;
    padding: 12px 16px;
    position: static;
  }

  .top-nav {
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .session-box {
    justify-content: space-between;
    padding-top: 2px;
  }
}

@media (max-width: 560px) {
  .brand-block p {
    display: none;
  }

  .top-nav a {
    flex: 0 0 auto;
  }

  .session-box {
    flex-wrap: wrap;
  }

  .user-name {
    max-width: 180px;
  }
}
</style>
