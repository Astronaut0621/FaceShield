<template>
  <div class="empty-state">
    <p>{{ message }}</p>
    <div v-if="$slots.action" class="empty-action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: '暂无数据'
  }
})
</script>

<style scoped>
.empty-state {
  display: grid;
  gap: 12px;
  place-items: center;
  padding: 40px 20px;
  color: var(--muted);
  text-align: center;
}

.empty-state p {
  margin: 0;
}

.empty-action :deep(button) {
  height: 36px;
  padding: 0 16px;
  border: 0;
  border-radius: 10px;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
}
</style>
