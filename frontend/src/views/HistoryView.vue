<template>
  <section class="page">
    <PageHeader title="History">
      <template #actions>
      <button @click="load">Refresh</button>
      </template>
    </PageHeader>
    <LoadingState :active="loading" />
    <InlineError :message="error" />
    <HistoryTable v-if="historyStore.items.length" :items="historyStore.items" />
    <EmptyState v-else-if="!loading" message="No records yet." />
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import HistoryTable from '../features/history/components/HistoryTable.vue'
import EmptyState from '../shared/components/EmptyState.vue'
import InlineError from '../shared/components/InlineError.vue'
import LoadingState from '../shared/components/LoadingState.vue'
import PageHeader from '../shared/components/PageHeader.vue'
import { listHistory } from '../features/history/services/history.service'
import { historyStore } from '../stores/history.store'
import { getApiErrorMessage } from '../utils/api-response'

const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  historyStore.setLoading(true)
  historyStore.setError('')
  try {
    const data = await listHistory({ page: 1, page_size: 20 })
    historyStore.setList(data)
  } catch (err) {
    const message = getApiErrorMessage(err, 'Failed to load history.')
    error.value = message
    historyStore.setError(message)
  } finally {
    loading.value = false
    historyStore.setLoading(false)
  }
}

onMounted(load)
</script>
