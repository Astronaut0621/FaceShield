<template>
  <section class="page detail-page">
    <PageHeader :title="`记录详情 #${route.params.id}`" description="查看单条检测的完整结果与可视化分析。">
      <template #actions>
        <BackHomeLink />
        <button class="secondary-btn" @click="router.push('/history')">返回列表</button>
      </template>
    </PageHeader>

    <LoadingState :active="loading" message="加载记录详情..." />
    <InlineError :message="error" />
    <DetectionResultPanel v-if="result && !loading" :result="result" />
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetectionResultPanel from '@/features/detection/components/result/DetectionResultPanel.vue'
import { getHistoryDetail } from '@/features/history/services/history.service'
import InlineError from '@/shared/components/InlineError.vue'
import LoadingState from '@/shared/components/LoadingState.vue'
import PageHeader from '@/shared/components/PageHeader.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import { getApiErrorMessage } from '@/utils/api-response'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const result = ref(null)

async function loadDetail() {
  const taskId = Number(route.params.id)
  if (!taskId) {
    error.value = '无效的记录编号。'
    return
  }

  loading.value = true
  error.value = ''
  try {
    result.value = await getHistoryDetail(taskId)
  } catch (err) {
    error.value = getApiErrorMessage(err, '加载记录详情失败。')
  } finally {
    loading.value = false
  }
}

onMounted(loadDetail)
watch(() => route.params.id, loadDetail)
</script>

<style scoped>
.detail-page {
  max-width: 960px;
}
</style>
