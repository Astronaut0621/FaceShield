<template>
  <header class="home-nav">
    <RouterLink class="brand" to="/">
      <img class="brand-mark" src="/images/logo.png" alt="" aria-hidden="true" />
      <span>FaceShield</span>
    </RouterLink>

    <div class="nav-actions">
      <nav class="nav-links" aria-label="首页导航">
        <RouterLink v-for="item in navigationItems" :key="item.name" :to="item.path">
          {{ item.label }}
        </RouterLink>
      </nav>
      <span v-if="authStore.isAuthenticated" class="user-name">{{ displayName }}</span>
      <button v-if="authStore.isAuthenticated" class="session-action" @click="signOut">
        退出登录
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { navigationItems } from '@/constants/routes'
import { logout } from '@/features/auth/services/auth.service'
import { authStore } from '@/stores/auth.store'

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
.home-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  min-height: 68px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(216, 224, 236, 0.76);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: var(--text);
  font-size: 18px;
  font-weight: 800;
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
}

.nav-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-links a {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  color: var(--muted-strong);
  text-decoration: none;
  font-size: 14px;
  font-weight: 650;
  transition:
    background 0.16s ease,
    color 0.16s ease;
}

.nav-links a:hover,
.nav-links a.router-link-active {
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

@media (max-width: 760px) {
  .home-nav {
    min-height: 62px;
    padding: 12px 14px;
  }

  .nav-actions {
    display: none;
  }
}
</style>
