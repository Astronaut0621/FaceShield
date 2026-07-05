<template>
  <header class="home-nav">
    <RouterLink class="brand" to="/">
      <svg class="brand-icon" viewBox="0 0 32 32" aria-hidden="true">
        <path
          d="M16 4L4 26h24L16 4zm0 6.5l6.8 13.5H9.2L16 10.5z"
          fill="currentColor"
        />
      </svg>
      <span>FaceShield</span>
    </RouterLink>

    <nav class="nav-links">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/detective">图片检测</RouterLink>
      <RouterLink to="/history">历史记录</RouterLink>
      <a href="#features">功能介绍</a>
    </nav>
  </header>
</template>

<script setup>
import { authStore } from '@/stores/auth.store'
</script>

<style scoped>
.home-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 14px 28px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.6);
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: #166534;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.brand-icon {
  width: 28px;
  height: 28px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-links a {
  color: #334155;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.15s;
}

.nav-links a:hover,
.nav-links a.router-link-active {
  color: #166534;
}

.login-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 0 22px;
  border-radius: 8px;
  background: #166534;
  color: #fff;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.15s;
}

.login-btn:hover {
  background: #15803d;
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }
}
</style>
