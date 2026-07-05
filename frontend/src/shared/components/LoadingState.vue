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
    default: '加载中…'
  }
})
</script>

<style scoped>
.loading-state {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  color: #475569;
  font-size: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(71, 85, 105, 0.25);
  border-top-color: #475569;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
