<template>
  <div class="app-shell app-page-shell">
    <div class="app-frame">
      <header class="topbar">
        <RouterLink class="brand-block" to="/">
          <img class="brand-mark" src="/images/logo.png" alt="" aria-hidden="true" />
          <span class="brand-name">{{ appConfig.name }}</span>
        </RouterLink>

        <div class="topbar-actions">
          <nav class="top-nav" aria-label="主导航">
            <RouterLink
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.path"
              :class="{ active: route.name === item.name }"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
          <span v-if="authStore.isAuthenticated" class="user-name">{{ displayName }}</span>
          <button v-if="authStore.isAuthenticated" class="session-action" @click="signOut">
            退出登录
          </button>
        </div>
      </header>
      <main class="app-main">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { appConfig } from '@/config/app.config'
import { navigationItems } from '@/constants/routes'
import { logout } from '@/features/auth/services/auth.service'
import { authStore } from '@/stores/auth.store'

const route = useRoute()
const displayName = computed(() => authStore.user?.display_name || authStore.user?.username || '当前用户')

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
.app-page-shell {
  min-height: 100dvh;
  padding: 18px;
  background: transparent;
}

.app-frame {
  min-height: calc(100dvh - 36px);
  overflow: hidden;
  border: 1px solid rgba(216, 224, 236, 0.9);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(247, 249, 252, 0.92)),
    var(--surface);
  box-shadow: var(--shadow);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 68px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(216, 224, 236, 0.76);
}

.brand-block {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  font-size: 18px;
  font-weight: 800;
  min-width: 0;
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: block;
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 50%;
  background: #fff;
  object-fit: cover;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.14);
  flex-shrink: 0;
}

.brand-name {
  white-space: nowrap;
}

.topbar-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
}

.top-nav a {
  display: inline-flex;
  align-items: center;
  height: 38px;
  color: var(--muted-strong);
  text-decoration: none;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 650;
  transition:
    background 0.16s ease,
    color 0.16s ease;
}

.top-nav a:hover {
  background: var(--accent-soft);
  color: var(--accent);
}

.top-nav a.router-link-active,
.top-nav a.active {
  background: var(--accent-soft);
  color: var(--accent);
}

.user-name {
  max-width: 120px;
  padding: 0 4px;
  color: var(--text);
  font-size: 14px;
  font-weight: 750;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-action {
  height: 38px;
  min-height: 38px;
  padding: 0 12px;
  border: 1px solid var(--line-strong);
  background: var(--surface);
  color: var(--muted-strong);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 650;
  white-space: nowrap;
  box-shadow: none;
}

.session-action:hover:not(:disabled) {
  background: var(--accent-soft);
  color: var(--accent);
  box-shadow: none;
}

.app-main {
  min-width: 0;
  width: min(1180px, calc(100% - 56px));
  margin: 0 auto;
  padding: 32px 0 48px;
  flex: 1;
}

@media (max-width: 980px) {
  .app-page-shell {
    padding: 10px;
  }

  .app-frame {
    min-height: calc(100dvh - 20px);
    border-radius: 20px;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
    padding: 12px 16px;
    position: static;
  }

  .topbar-actions {
    width: 100%;
    justify-content: flex-start;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .top-nav {
    justify-content: flex-start;
  }

  .app-main {
    width: min(100% - 32px, 1180px);
    padding: 22px 0 36px;
  }
}

@media (max-width: 560px) {
  .top-nav a {
    flex: 0 0 auto;
  }

  .user-name {
    flex: 0 0 auto;
  }

  .session-action {
    flex: 0 0 auto;
  }
}
</style>
