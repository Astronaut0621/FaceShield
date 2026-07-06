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
  min-height: 38px;
  padding: 0 14px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.94);
  color: var(--muted-strong);
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  transition:
    border-color 0.16s ease,
    color 0.16s ease,
    background 0.16s ease,
    transform 0.16s ease;
}

.back-home svg {
  width: 16px;
  height: 16px;
}

.back-home:hover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-soft);
  transform: translateY(-1px);
}
</style>
