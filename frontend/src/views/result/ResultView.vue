<template>
  <section class="page result-page">
    <PageHeader title="检测结果" description="查看伪造概率、风险等级与可疑区域热力图。">
      <template #actions>
        <BackHomeLink />
        <button class="secondary-btn" @click="router.push('/detective')">继续检测</button>
        <button class="secondary-btn" @click="router.push('/history')">历史记录</button>
      </template>
    </PageHeader>

    <LoadingState :active="loading" message="加载检测结果..." />
    <InlineError :message="error" />

    <DetectionResultPanel v-if="result && !loading" :result="result" />
    <EmptyState v-else-if="!loading && !error" message="暂无检测结果，请先上传图片进行检测。">
      <template #action>
        <button @click="router.push('/detective')">去上传图片</button>
      </template>
    </EmptyState>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetectionResultPanel from '@/features/detection/components/result/DetectionResultPanel.vue'
import { getDetectionDetail } from '@/features/detection/services/detection.service'
import EmptyState from '@/shared/components/EmptyState.vue'
import InlineError from '@/shared/components/InlineError.vue'
import LoadingState from '@/shared/components/LoadingState.vue'
import PageHeader from '@/shared/components/PageHeader.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import { detectionStore } from '@/stores/detection.store'
import { getApiErrorMessage } from '@/utils/api-response'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const error = ref('')
const fetchedResult = ref(null)

const result = computed(() => {
  const taskId = Number(route.params.id)
  if (
    detectionStore.latestResult &&
    Number(detectionStore.latestResult.taskId) === taskId
  ) {
    return detectionStore.latestResult
  }
  return fetchedResult.value
})

async function loadResult() {
  const taskId = Number(route.params.id)
  if (!taskId) {
    error.value = '无效的记录编号。'
    return
  }

  if (
    detectionStore.latestResult &&
    Number(detectionStore.latestResult.taskId) === taskId
  ) {
    return
  }

  loading.value = true
  error.value = ''
  try {
    fetchedResult.value = await getDetectionDetail(taskId)
  } catch (err) {
    error.value = getApiErrorMessage(err, '加载检测结果失败。')
  } finally {
    loading.value = false
  }
}

onMounted(loadResult)
watch(() => route.params.id, loadResult)
</script>

<style scoped>
.result-page {
  max-width: 1040px;
}
</style>
