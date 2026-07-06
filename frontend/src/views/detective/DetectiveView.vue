<template>
  <section class="detective-page">
    <header class="detective-banner">
      <div class="banner-content">
        <p class="banner-kicker">FaceShield · AI 换脸检测</p>
        <h1>图片检测工作台</h1>
        <p class="banner-desc">
          上传待检测人脸图片，选择检测模型后，系统将自动完成人脸裁剪、频域-空域融合推理，
          并输出伪造概率、风险等级与可疑区域热力图。
        </p>
        <div class="banner-tags">
          <span v-for="tag in tags" :key="tag">{{ tag }}</span>
        </div>
      </div>
      <BackHomeLink />
    </header>

    <div class="upload-section">
      <div class="upload-card">
        <h2>上传待检测图片</h2>

        <ModelSelector
          v-model="selectedModelId"
          :disabled="loading"
          @update:model-value="onModelChange"
        />

        <DetectionFileUploader
          v-model="detectionStore.currentFile"
          large
          :loading="loading"
          @submit="submit"
        />

        <Transition name="fade">
          <div v-if="loading" class="detecting-banner">
            <span class="spinner" />
            <div>
              <strong>正在分析图片</strong>
              <p>频域特征提取 → 空域纹理分析 → 融合推理中…</p>
            </div>
          </div>
        </Transition>

        <InlineError :message="error" />
      </div>
    </div>

    <DetectionGuidePanel class="guide-below" />
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import DetectionFileUploader from '@/features/detection/components/upload/DetectionFileUploader.vue'
import ModelSelector from '@/features/detection/components/upload/ModelSelector.vue'
import DetectionGuidePanel from '@/features/detection/components/DetectionGuidePanel.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import InlineError from '@/shared/components/InlineError.vue'
import { routeNames } from '@/constants/routes'
import { uploadAndDetect } from '@/features/detection/services/detection.service'
import { useAsyncTask } from '@/composables/useAsyncTask'
import { detectionStore } from '@/stores/detection.store'

const router = useRouter()
const { loading, error, run } = useAsyncTask()
const selectedModelId = ref(detectionStore.selectedModelId)

const tags = ['频域 FFT', '空域 CNN', 'Grad-CAM', '风险评级']

watch(loading, value => detectionStore.setLoading(value))
watch(error, value => detectionStore.setError(value))

function onModelChange(modelId) {
  detectionStore.setSelectedModelId(modelId || null)
}

async function submit() {
  if (!detectionStore.currentFile) return
  const result = await run(
    () => uploadAndDetect(detectionStore.currentFile, selectedModelId.value),
    '检测失败，请稍后重试。'
  )
  if (!result) return
  detectionStore.setResult(result)
  router.push({ name: routeNames.result, params: { id: String(result.taskId) } })
}
</script>

<style scoped>
.detective-page {
  max-width: 1000px;
  margin: 0 auto;
}

.detective-banner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
  padding: 28px 32px;
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.82) 0%, rgba(30, 27, 75, 0.72) 100%),
    url('https://images.unsplash.com/photo-1535378437324-bdad4cbb4615?auto=format&fit=crop&w=1200&q=80')
      center / cover no-repeat;
  color: #fff;
}

.banner-kicker {
  margin: 0 0 8px;
  font-size: 13px;
  letter-spacing: 0.06em;
  opacity: 0.85;
}

.detective-banner h1 {
  margin: 0 0 10px;
  font-size: 28px;
  font-weight: 700;
}

.banner-desc {
  margin: 0 0 16px;
  max-width: 560px;
  font-size: 14px;
  line-height: 1.7;
  opacity: 0.9;
}

.banner-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.banner-tags span {
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(4px);
  font-size: 12px;
  font-weight: 500;
}

.upload-section {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.upload-card {
  width: 100%;
  max-width: 1000px;
  background: #fff;
  border: 1px solid #dbe3ec;
  border-radius: 16px;
  padding: 32px 36px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
}

.upload-card h2 {
  margin: 0 0 8px;
  font-size: 20px;
  color: #0f172a;
  text-align: center;
}

.guide-below {
  max-width: 760px;
  margin: 0 auto;
}

.detecting-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-top: 20px;
  padding: 16px 18px;
  border-radius: 10px;
  background: linear-gradient(135deg, #eff6ff, #f0fdf4);
  border: 1px solid #bfdbfe;
  color: #1e40af;
}

.detecting-banner strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
}

.detecting-banner p {
  margin: 0;
  font-size: 13px;
  color: #3b82f6;
}

.spinner {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-top: 2px;
  border: 2px solid rgba(29, 78, 216, 0.25);
  border-top-color: #1d4ed8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .detective-banner {
    flex-direction: column;
    padding: 24px 20px;
  }

  .upload-card {
    padding: 24px 20px;
  }
}
</style>
