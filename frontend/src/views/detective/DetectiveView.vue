<template>
  <section class="detective-page">
    <header class="detective-banner">
      <div class="banner-content">
        <p class="banner-kicker">FaceShield AI 换脸检测</p>
        <h1>图片检测工作台</h1>
        <p class="banner-desc">
          上传待检测人脸图片，系统将完成人脸裁剪、频域与空域融合推理，并输出伪造概率、风险等级与热力图。
        </p>
        <div class="banner-tags">
          <span v-for="tag in tags" :key="tag">{{ tag }}</span>
        </div>
      </div>
      <BackHomeLink />
    </header>

    <div class="detective-grid">
      <div class="upload-column">
        <div class="upload-card">
          <div class="card-heading">
            <h2>上传待检测图片</h2>
            <p>推荐使用清晰、正面、无遮挡的人脸图片。</p>
          </div>
          <DetectionFileUploader
            v-model="detectionStore.currentFile"
            :loading="loading"
            @submit="submit"
          />

          <Transition name="fade">
            <div v-if="loading" class="detecting-banner">
              <span class="spinner" />
              <div>
                <strong>正在分析图片</strong>
                <p>频域特征提取 / 空域纹理分析 / 融合推理中...</p>
              </div>
            </div>
          </Transition>

          <InlineError :message="error" />
        </div>
      </div>

      <DetectionGuidePanel />
    </div>
  </section>
</template>

<script setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import DetectionFileUploader from '@/features/detection/components/upload/DetectionFileUploader.vue'
import DetectionGuidePanel from '@/features/detection/components/DetectionGuidePanel.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import InlineError from '@/shared/components/InlineError.vue'
import { routeNames } from '@/constants/routes'
import { uploadAndDetect } from '@/features/detection/services/detection.service'
import { useAsyncTask } from '@/composables/useAsyncTask'
import { detectionStore } from '@/stores/detection.store'

const router = useRouter()
const { loading, error, run } = useAsyncTask()

const tags = ['频域 FFT', '空域 CNN', 'Grad-CAM', '风险评级']

watch(loading, value => detectionStore.setLoading(value))
watch(error, value => detectionStore.setError(value))

async function submit() {
  if (!detectionStore.currentFile) return
  const result = await run(
    () => uploadAndDetect(detectionStore.currentFile),
    '检测失败，请稍后重试。'
  )
  if (!result) return
  detectionStore.setResult(result)
  router.push({ name: routeNames.result, params: { id: String(result.taskId) } })
}
</script>

<style scoped>
.detective-page {
  max-width: 1160px;
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
    linear-gradient(135deg, rgba(9, 24, 19, 0.92), rgba(8, 116, 67, 0.78)),
    url('/images/home-hero-bg.png') center / cover no-repeat;
  color: #fff;
  box-shadow: 0 20px 60px rgba(16, 35, 27, 0.16);
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
  max-width: 650px;
  font-size: 15px;
  line-height: 1.75;
  color: rgba(255, 255, 255, 0.84);
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
  grid-template-columns: minmax(0, 1.24fr) minmax(320px, 0.76fr);
  gap: 18px;
  align-items: start;
}

.upload-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d8e4de;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 16px 42px rgba(16, 35, 27, 0.07);
}

.card-heading {
  display: grid;
  gap: 6px;
  margin-bottom: 18px;
}

.card-heading h2 {
  margin: 0;
  font-size: 20px;
  color: #10231b;
}

.card-heading p {
  margin: 0;
  color: #60756b;
  font-size: 13px;
}

.detecting-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-top: 18px;
  padding: 16px 18px;
  border-radius: 14px;
  background: #e1f4eb;
  border: 1px solid #b9e4cf;
  color: #065f36;
}

.detecting-banner strong {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
}

.detecting-banner p {
  margin: 0;
  font-size: 13px;
  color: #087443;
}

.spinner {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-top: 2px;
  border: 2px solid rgba(8, 116, 67, 0.22);
  border-top-color: #087443;
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

  .detective-grid {
    grid-template-columns: 1fr;
  }
}
</style>
