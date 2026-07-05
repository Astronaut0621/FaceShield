<template>
  <section class="page">
    <PageHeader
      title="Image Detection"
      description="Upload one image and run the current mock detector."
    />
    <DetectionFileUploader v-model="detectionStore.currentFile" :loading="loading" @submit="submit" />
    <InlineError :message="error" />
    <DetectionResultCard :result="detectionStore.latestResult" />
  </section>
</template>

<script setup>
import { watch } from 'vue'
import DetectionFileUploader from '../features/detection/components/DetectionFileUploader.vue'
import DetectionResultCard from '../features/detection/components/DetectionResultCard.vue'
import InlineError from '../shared/components/InlineError.vue'
import PageHeader from '../shared/components/PageHeader.vue'
import { uploadAndDetect } from '../features/detection/services/detection.service'
import { useAsyncTask } from '../composables/useAsyncTask'
import { detectionStore } from '../stores/detection.store'

const { loading, error, run } = useAsyncTask()

watch(loading, value => detectionStore.setLoading(value))
watch(error, value => detectionStore.setError(value))

async function submit() {
  if (!detectionStore.currentFile) return
  const result = await run(
    () => uploadAndDetect(detectionStore.currentFile),
    'Detection failed.'
  )
  detectionStore.setResult(result)
}
</script>
