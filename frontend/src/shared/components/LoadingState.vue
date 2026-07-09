<template>
  <div v-if="active" class="loading-state">
    <span class="spinner" />
    <span>{{ message }}</span>
  </div>
</template>

<script setup>
defineProps({
  active: Boolean,
  message: {
    type: String,
    default: '加载中...'
  }
})
</script>

<style scoped>
.loading-state {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  width: fit-content;
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid rgba(37, 99, 235, 0.12);
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--muted);
  font-size: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(37, 99, 235, 0.22);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
