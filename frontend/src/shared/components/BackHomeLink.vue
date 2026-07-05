<template>
  <RouterLink class="back-home" to="/">
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M10 19l-7-7m0 0l7-7m-7 7h18"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    返回首页
  </RouterLink>
</template>

<style scoped>
.back-home {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 14px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #fff;
  color: #334155;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}

.back-home svg {
  width: 16px;
  height: 16px;
}

.back-home:hover {
  border-color: #166534;
  color: #166534;
  background: #f0fdf4;
}
</style>
