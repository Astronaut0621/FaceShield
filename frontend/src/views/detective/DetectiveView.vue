<template>
  <section class="detective-page">
    <header class="detective-banner">
      <div class="banner-content">
        <p class="banner-kicker">FaceShield AI 换脸检测</p>
        <h1>图片检测工作台</h1>
        <p class="banner-desc">
          上传待检测人脸图片，选择检测模型后，系统将自动完成人脸裁剪、频域与空域融合推理，并输出伪造概率、风险等级与热力图。
        </p>
        <div class="banner-tags" aria-label="检测能力">
          <span v-for="tag in tags" :key="tag">{{ tag }}</span>
        </div>
      </div>
      <BackHomeLink />
    </header>

    <div class="detective-grid">
      <div class="upload-card">
        <div class="card-heading">
          <h2>上传待检测图片</h2>
          <p>推荐使用清晰、正面、无遮挡的人脸图片。</p>
        </div>

        <ModelSelector
          v-model="selectedModelId"
          :disabled="loading"
          @update:model-value="onModelChange"
        />

        <template v-if="isAssetMode">
          <div class="asset-detect-panel">
            <div class="asset-preview">
              <img v-if="asset?.file_url" :src="resolveStorageUrl(asset.file_url)" alt="检测资产预览" />
              <div class="asset-info">
                <strong>{{ asset?.original_filename || '已选资产图片' }}</strong>
                <p>{{ asset ? formatAssetMeta(asset) : '正在加载资产...' }}</p>
              </div>
            </div>
            <button class="primary-btn" :disabled="loading" @click="submit">
              {{ loading ? '检测中，请稍候...' : '使用该资产开始检测' }}
            </button>
          </div>
        </template>

        <DetectionFileUploader
          v-else
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
              <p>频域特征提取、空域纹理分析、融合推理中...</p>
            </div>
          </div>
        </Transition>

        <InlineError :message="error" />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DetectionFileUploader from '@/features/detection/components/upload/DetectionFileUploader.vue'
import ModelSelector from '@/features/detection/components/upload/ModelSelector.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import InlineError from '@/shared/components/InlineError.vue'
import { routeNames } from '@/constants/routes'
import { uploadAndDetect, startDetection } from '@/features/detection/services/detection.service'
import { getAsset } from '@/features/assets/services/asset.service'
import { useAsyncTask } from '@/composables/useAsyncTask'
import { detectionStore } from '@/stores/detection.store'
import { resolveStorageUrl } from '@/utils/storage'
import { formatFileSize } from '@/utils/formatters'

const router = useRouter()
const route = useRoute()
const { loading, error, run } = useAsyncTask()
const selectedModelId = ref(detectionStore.selectedModelId)
const assetId = ref(null)
const asset = ref(null)

const isAssetMode = computed(() => Boolean(asset.value && assetId.value))

const tags = ['频域 FFT', '空域 CNN', '热力图解释', '风险评级']

watch(loading, value => detectionStore.setLoading(value))
watch(error, value => detectionStore.setError(value))

watch(
  () => route.query.asset,
  async assetValue => {
    if (!assetValue) return
    const id = Number(assetValue)
    if (!id || assetId.value === id) return

    assetId.value = id
    await loadAsset(id)
  },
  { immediate: true }
)

function onModelChange(modelId) {
  detectionStore.setSelectedModelId(modelId || null)
}

async function loadAsset(id) {
  const record = await run(() => getAsset(id), '加载资产内容失败。')
  if (!record) {
    asset.value = null
    assetId.value = null
    return
  }
  asset.value = record
  // 使用资产模式时，清空上传文件，避免需要重新上传
  detectionStore.setFile(null)
}

function formatAssetMeta(asset) {
  return `${formatFileSize(asset.file_size)} · ${asset.file_type?.toUpperCase() || 'IMG'}`
}

async function submit() {
  if (isAssetMode.value) {
    if (!assetId.value) return
    const result = await run(
      () => startDetection(assetId.value, selectedModelId.value),
      '检测失败，请稍后重试。'
    )
    if (!result) return
    detectionStore.setResult(result)
    router.push({ name: routeNames.result, params: { id: String(result.taskId) } })
    return
  }

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
  margin-bottom: 22px;
  padding: 30px;
  border-radius: 22px;
  background:
    linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(37, 99, 235, 0.76)),
    url('/images/home-hero-bg.png') center / cover no-repeat;
  color: #fff;
  box-shadow: 0 20px 60px rgba(23, 32, 51, 0.16);
}

.banner-kicker {
  width: fit-content;
  margin: 0 0 10px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.13);
  color: rgba(255, 255, 255, 0.88);
  font-size: 12px;
  font-weight: 750;
}

.detective-banner h1 {
  margin: 0 0 10px;
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 850;
  letter-spacing: -0.02em;
}

.banner-desc {
  margin: 0 0 18px;
  max-width: 680px;
  font-size: 15px;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.86);
}

.banner-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.banner-tags span {
  padding: 6px 11px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.16);
  font-size: 12px;
  font-weight: 700;
}

.detective-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}

.upload-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 16px 42px rgba(23, 32, 51, 0.07);
}

.card-heading {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}

.card-heading h2 {
  margin: 0;
  font-size: 20px;
  color: var(--text);
}

.card-heading p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.detecting-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--accent-soft);
  border: 1px solid #c7d7fe;
  color: var(--accent-strong);
}

.detecting-banner strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
}

.detecting-banner p {
  margin: 0;
  font-size: 13px;
  color: var(--accent);
}

.spinner {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-top: 2px;
  border: 2px solid rgba(37, 99, 235, 0.22);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
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

@media (max-width: 980px) {
  .detective-banner {
    flex-direction: column;
    padding: 24px 20px;
  }

  .upload-card {
    padding: 24px 20px;
  }
}
</style>
