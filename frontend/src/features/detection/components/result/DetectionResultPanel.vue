<template>
  <section v-if="result" class="result-panel">
    <header class="result-header">
      <div>
        <p class="result-kicker">检测结果</p>
        <h3 :class="['verdict', result.label]">{{ formatLabel(result.label) }}</h3>
      </div>
      <ProbabilityGauge :value="result.fakeProbability" :risk-level="result.riskLevel" />
    </header>

    <div class="result-meta">
      <div class="meta-item">
        <span>风险等级</span>
        <RiskBadge :level="result.riskLevel" />
      </div>
      <div class="meta-item">
        <span>记录编号</span>
        <strong>#{{ result.taskId || '-' }}</strong>
      </div>
      <div class="meta-item">
        <span>检测时间</span>
        <strong>{{ formatDateTime(result.createdAt) }}</strong>
      </div>
      <div v-if="result.modelVersion" class="meta-item">
        <span>模型版本</span>
        <strong>{{ result.modelVersion }}</strong>
      </div>
    </div>

    <div class="score-grid">
      <ScoreBar label="空域特征分数" :value="result.spatialScore" tone="spatial" />
      <ScoreBar label="频域特征分数" :value="result.frequencyScore" tone="frequency" />
    </div>

    <p v-if="result.suggestion" class="suggestion">{{ result.suggestion }}</p>

    <div class="image-grid">
      <figure class="image-card">
        <figcaption>原始图片</figcaption>
        <img
          v-if="result.originalImageUrl"
          :src="resolveStorageUrl(result.originalImageUrl)"
          alt="原始图片"
        />
        <div v-else class="image-empty">暂无原图</div>
      </figure>

      <figure class="image-card">
        <figcaption>人脸裁剪</figcaption>
        <img
          v-if="result.faceCropUrl"
          :src="resolveStorageUrl(result.faceCropUrl)"
          alt="人脸裁剪图"
        />
        <div v-else class="image-empty">
          {{ result.faceDetected === false ? '未检测到人脸' : '暂无人脸裁剪图' }}
        </div>
      </figure>
    </div>

    <HeatmapViewer
      :base-image-url="result.faceCropUrl || result.originalImageUrl"
      :heatmap-url="result.heatmapUrl"
      :fallback-image-url="result.originalImageUrl"
    />
  </section>
</template>

<script setup>
import HeatmapViewer from './HeatmapViewer.vue'
import ProbabilityGauge from './ProbabilityGauge.vue'
import RiskBadge from './RiskBadge.vue'
import ScoreBar from './ScoreBar.vue'
import { formatDateTime, formatLabel } from '@/utils/formatters'
import { resolveStorageUrl } from '@/utils/storage'

defineProps({
  result: {
    type: Object,
    default: null
  }
})
</script>

<style scoped>
.result-panel {
  display: grid;
  gap: 24px;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d8e4de;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 16px 42px rgba(16, 35, 27, 0.07);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.result-kicker {
  margin: 0 0 4px;
  color: #60756b;
  font-size: 13px;
  font-weight: 750;
}

.verdict {
  margin: 0;
  font-size: 28px;
}

.verdict.real {
  color: #087443;
}

.verdict.fake {
  color: #b42318;
}

.result-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  padding: 16px;
  background: #f6faf8;
  border: 1px solid #e5eee9;
  border-radius: 16px;
}

.meta-item {
  display: grid;
  gap: 6px;
}

.meta-item span {
  color: #60756b;
  font-size: 13px;
}

.meta-item strong {
  color: #10231b;
}

.score-grid {
  display: grid;
  gap: 16px;
}

.suggestion {
  margin: 0;
  padding: 14px 16px;
  border-left: 4px solid #087443;
  background: #e1f4eb;
  color: #065f36;
  border-radius: 0 12px 12px 0;
  line-height: 1.6;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.image-card {
  margin: 0;
  display: grid;
  gap: 10px;
}

.image-card figcaption {
  font-size: 14px;
  font-weight: 600;
  color: #33463d;
}

.image-card img {
  width: 100%;
  max-height: 280px;
  object-fit: contain;
  border-radius: 16px;
  background: #10231b;
  border: 1px solid #d8e4de;
}

.image-empty {
  display: grid;
  place-items: center;
  min-height: 180px;
  border: 1px dashed #bfd0c7;
  border-radius: 16px;
  background: #f6faf8;
  color: #60756b;
  font-size: 14px;
  text-align: center;
  padding: 16px;
}
</style>
