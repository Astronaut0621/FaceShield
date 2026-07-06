<template>
  <header class="home-nav">
    <RouterLink class="brand" to="/">
      <span class="brand-mark" aria-hidden="true">F</span>
      <span>FaceShield</span>
    </RouterLink>

    <nav class="nav-links" aria-label="首页导航">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/detective">图片检测</RouterLink>
      <RouterLink to="/history">历史记录</RouterLink>
      <a href="#features">功能介绍</a>
    </nav>
  </header>
</template>

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
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: var(--accent);
  color: #fff;
  font-size: 16px;
  font-weight: 900;
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

@media (max-width: 760px) {
  .home-nav {
    min-height: 62px;
    padding: 12px 14px;
  }

  .nav-links {
    display: none;
  }
}
</style>
