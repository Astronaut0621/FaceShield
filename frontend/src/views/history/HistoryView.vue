<template>
  <section class="page history-page">
    <PageHeader title="历史记录" description="查看您的历史检测记录，点击条目可查看完整详情。">
      <template #actions>
        <BackHomeLink />
        <button :disabled="loading" @click="load">刷新</button>
      </template>
    </PageHeader>

    <div class="filters">
      <label>
        结论
        <select v-model="filters.label" @change="onFilterChange">
          <option value="">全部</option>
          <option value="real">真实人脸</option>
          <option value="fake">伪造人脸</option>
        </select>
      </label>
      <label>
        风险等级
        <select v-model="filters.riskLevel" @change="onFilterChange">
          <option value="">全部</option>
          <option value="low">低风险</option>
          <option value="medium">中风险</option>
          <option value="high">高风险</option>
        </select>
      </label>
    </div>

    <LoadingState :active="loading" message="加载历史记录…" />
    <InlineError :message="error" />

    <HistoryTable v-if="historyStore.items.length" :items="historyStore.items" />
    <EmptyState v-else-if="!loading" message="暂无检测记录，上传图片开始第一次检测吧。">
      <template #action>
        <button @click="router.push('/detective')">去检测</button>
      </template>
    </EmptyState>

    <Pagination
      v-model:page="page"
      :page-size="pageSize"
      :total="historyStore.total"
      @update:page="load"
    />
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import HistoryTable from '@/features/history/components/HistoryTable.vue'
import EmptyState from '@/shared/components/EmptyState.vue'
import InlineError from '@/shared/components/InlineError.vue'
import LoadingState from '@/shared/components/LoadingState.vue'
import PageHeader from '@/shared/components/PageHeader.vue'
import Pagination from '@/shared/components/Pagination.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import { listHistory } from '@/features/history/services/history.service'
import { historyStore } from '@/stores/history.store'
import { getApiErrorMessage } from '@/utils/api-response'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const page = ref(1)
const pageSize = 10

const filters = reactive({
  label: '',
  riskLevel: ''
})

async function load() {
  loading.value = true
  error.value = ''
  historyStore.setLoading(true)
  historyStore.setError('')
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }
    if (filters.label) params.label = filters.label
    if (filters.riskLevel) params.risk_level = filters.riskLevel

    const data = await listHistory(params)
    historyStore.setList(data)
  } catch (err) {
    const message = getApiErrorMessage(err, '加载历史记录失败。')
    error.value = message
    historyStore.setError(message)
  } finally {
    loading.value = false
    historyStore.setLoading(false)
  }
}

function onFilterChange() {
  page.value = 1
  load()
}

onMounted(load)
</script>

<style scoped>
.history-page {
  max-width: 1120px;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid #d8e4de;
  border-radius: 16px;
}

.filters label {
  display: grid;
  gap: 6px;
  font-size: 13px;
  color: #33463d;
  font-weight: 700;
}

.filters select {
  height: 36px;
  min-width: 140px;
  border: 1px solid #bfd0c7;
  border-radius: 10px;
  padding: 0 10px;
  background: #fff;
  font: inherit;
}
</style>
