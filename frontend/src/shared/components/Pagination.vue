<template>
  <div v-if="totalPages > 1" class="pagination" aria-label="分页导航">
    <button :disabled="page <= 1" @click="goToPage(page - 1)">上一页</button>
    <span class="page-status">第 {{ page }} / {{ totalPages }} 页（共 {{ total }} 条）</span>
    <button :disabled="page >= totalPages" @click="goToPage(page + 1)">下一页</button>

    <form class="page-jump" @submit.prevent="jumpToInputPage">
      <label>
        跳至
        <input
          v-model.number="inputPage"
          type="number"
          inputmode="numeric"
          :min="1"
          :max="totalPages"
          @blur="syncInputPage"
        />
        页
      </label>
      <button type="submit">跳转</button>
    </form>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

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

const emit = defineEmits(['update:page'])
const inputPage = ref(props.page)

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

watch(
  () => props.page,
  value => {
    inputPage.value = value
  }
)

function normalizePage(value) {
  const pageNumber = Number(value)
  if (!Number.isFinite(pageNumber)) {
    return props.page
  }
  return Math.min(totalPages.value, Math.max(1, Math.trunc(pageNumber)))
}

function goToPage(value) {
  const nextPage = normalizePage(value)
  inputPage.value = nextPage
  if (nextPage !== props.page) {
    emit('update:page', nextPage)
  }
}

function jumpToInputPage() {
  goToPage(inputPage.value)
}

function syncInputPage() {
  inputPage.value = normalizePage(inputPage.value)
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 20px;
}

.page-status {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1;
  white-space: nowrap;
}

.pagination button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  min-width: 76px;
  padding: 0 16px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
  color: var(--muted-strong);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  line-height: 1;
}

.page-jump {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.page-jump label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 40px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1;
  white-space: nowrap;
}

.page-jump input {
  box-sizing: border-box;
  width: 72px;
  height: 40px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  padding: 0 10px;
  background: var(--surface);
  color: var(--text);
  font: inherit;
  font-variant-numeric: tabular-nums;
  line-height: 40px;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .pagination {
    align-items: stretch;
  }

  .page-status,
  .page-jump {
    width: 100%;
    justify-content: center;
  }
}
</style>
