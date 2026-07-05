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
  background: #fff;
  border: 1px solid #dbe3ec;
  border-radius: 12px;
  padding: 24px;
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
  color: #64748b;
  font-size: 13px;
}

.verdict {
  margin: 0;
  font-size: 28px;
}

.verdict.real {
  color: #15803d;
}

.verdict.fake {
  color: #b91c1c;
}

.result-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.meta-item {
  display: grid;
  gap: 6px;
}

.meta-item span {
  color: #64748b;
  font-size: 13px;
}

.score-grid {
  display: grid;
  gap: 16px;
}

.suggestion {
  margin: 0;
  padding: 14px 16px;
  border-left: 4px solid #6366f1;
  background: #eef2ff;
  color: #3730a3;
  border-radius: 0 8px 8px 0;
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
  color: #334155;
}

.image-card img {
  width: 100%;
  max-height: 280px;
  object-fit: contain;
  border-radius: 10px;
  background: #0f172a;
  border: 1px solid #e2e8f0;
}

.image-empty {
  display: grid;
  place-items: center;
  min-height: 180px;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
  color: #64748b;
  font-size: 14px;
  text-align: center;
  padding: 16px;
}
</style>
