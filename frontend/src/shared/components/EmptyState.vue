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
  border: 1px dashed var(--line-strong);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(247, 249, 252, 0.9), rgba(255, 255, 255, 0.96)),
    var(--surface);
  color: var(--muted);
  text-align: center;
}

.empty-state p {
  margin: 0;
}

.empty-action :deep(button) {
  min-height: 40px;
  padding: 0 16px;
  border-radius: 12px;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  font-weight: 750;
}
</style>
