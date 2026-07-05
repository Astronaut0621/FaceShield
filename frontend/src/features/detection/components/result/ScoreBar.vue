<template>
  <div class="score-bar">
    <div class="score-bar-header">
      <span>{{ label }}</span>
      <strong>{{ formatPercent(value, 1) }}</strong>
    </div>
    <div class="score-bar-track">
      <div class="score-bar-fill" :class="tone" :style="{ width: barWidth }" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatPercent } from '@/utils/formatters'

const props = defineProps({
  label: String,
  value: {
    type: Number,
    default: null
  },
  tone: {
    type: String,
    default: 'spatial'
  }
})

const barWidth = computed(() => {
  if (props.value === null || props.value === undefined) return '0%'
  const num = Number(props.value)
  const percent = num <= 1 ? num * 100 : num
  return `${Math.min(Math.max(percent, 0), 100)}%`
})
</script>

<style scoped>
.score-bar {
  display: grid;
  gap: 8px;
}

.score-bar-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #475569;
}

.score-bar-track {
  height: 8px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 0.5s ease;
}

.score-bar-fill.spatial {
  background: linear-gradient(90deg, #3b82f6, #6366f1);
}

.score-bar-fill.frequency {
  background: linear-gradient(90deg, #8b5cf6, #a855f7);
}
</style>
