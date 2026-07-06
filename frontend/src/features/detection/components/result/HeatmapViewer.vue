<template>
  <section class="heatmap-viewer">
    <div class="heatmap-toolbar">
      <span class="section-label">可疑区域热力图</span>
      <label v-if="hasHeatmap" class="overlay-toggle">
        <input v-model="showOverlay" type="checkbox" />
        叠加显示
      </label>
    </div>

    <div v-if="hasHeatmap" class="heatmap-stage" :class="{ overlay: showOverlay }">
      <img
        class="base-image"
        :src="baseImageSrc"
        alt="检测基准图"
        @error="onBaseError"
      />
      <img
        v-show="showOverlay"
        class="heatmap-image"
        :src="heatmapSrc"
        alt="Grad-CAM 热力图"
        @error="onHeatmapError"
      />
    </div>

    <div v-else class="heatmap-placeholder">
      <div class="placeholder-icon">CAM</div>
      <p>暂无可疑区域热力图</p>
      <span>模型联调后将展示热力图可视化结果</span>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { resolveStorageUrl } from '@/utils/storage'

const props = defineProps({
  baseImageUrl: String,
  heatmapUrl: String,
  fallbackImageUrl: String
})

const showOverlay = ref(true)
const baseError = ref(false)
const heatmapError = ref(false)

const baseImageSrc = computed(() => {
  if (baseError.value && props.fallbackImageUrl) {
    return resolveStorageUrl(props.fallbackImageUrl)
  }
  return resolveStorageUrl(props.baseImageUrl || props.fallbackImageUrl)
})

const heatmapSrc = computed(() => resolveStorageUrl(props.heatmapUrl))

const hasHeatmap = computed(() => Boolean(props.heatmapUrl) && !heatmapError.value)

function onBaseError() {
  baseError.value = true
}

function onHeatmapError() {
  heatmapError.value = true
}
</script>

<style scoped>
.heatmap-viewer {
  display: grid;
  gap: 12px;
}

.heatmap-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--muted-strong);
}

.overlay-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--muted);
  cursor: pointer;
}

.heatmap-stage {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: var(--text);
  min-height: 260px;
  display: grid;
  place-items: center;
}

.heatmap-stage img {
  max-width: 100%;
  max-height: 360px;
  object-fit: contain;
}

.heatmap-stage.overlay .heatmap-image {
  position: absolute;
  inset: 0;
  margin: auto;
  opacity: 0.62;
  mix-blend-mode: screen;
}

.heatmap-placeholder {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 220px;
  border: 1px dashed var(--line-strong);
  border-radius: 10px;
  background: var(--surface-soft);
  text-align: center;
  padding: 24px;
}

.placeholder-icon {
  width: 48px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 12px;
  font-weight: 900;
}

.heatmap-placeholder p {
  margin: 0;
  font-weight: 700;
  color: var(--muted-strong);
}

.heatmap-placeholder span {
  color: var(--muted);
  font-size: 13px;
}
</style>
