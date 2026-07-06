<template>
  <div v-if="totalPages > 1" class="pagination">
    <button :disabled="page <= 1" @click="$emit('update:page', page - 1)">上一页</button>
    <span>第 {{ page }} / {{ totalPages }} 页（共 {{ total }} 条）</span>
    <button :disabled="page >= totalPages" @click="$emit('update:page', page + 1)">下一页</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    default: 0
  }
})

defineEmits(['update:page'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
}

.pagination span {
  color: var(--muted);
  font-size: 14px;
}

.pagination button {
  height: 36px;
  padding: 0 14px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
  color: var(--muted-strong);
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
