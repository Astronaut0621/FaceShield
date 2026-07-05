<template>
  <div class="gauge" :class="riskLevelClass(riskLevel)">
    <svg viewBox="0 0 120 120" aria-hidden="true">
      <circle class="gauge-track" cx="60" cy="60" r="52" />
      <circle
        class="gauge-fill"
        cx="60"
        cy="60"
        r="52"
        :stroke-dasharray="`${circumference} ${circumference}`"
        :stroke-dashoffset="dashOffset"
      />
    </svg>
    <div class="gauge-center">
      <strong>{{ displayPercent }}</strong>
      <span>伪造概率</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatPercent, riskLevelClass } from '@/utils/formatters'

const props = defineProps({
  value: {
    type: Number,
    default: null
  },
  riskLevel: {
    type: String,
    default: ''
  }
})

const radius = 52
const circumference = 2 * Math.PI * radius

const normalized = computed(() => {
  if (props.value === null || props.value === undefined) return 0
  const num = Number(props.value)
  return num <= 1 ? num : num / 100
})

const dashOffset = computed(() => circumference * (1 - normalized.value))

const displayPercent = computed(() => formatPercent(props.value, 1))
</script>

<style scoped>
.gauge {
  position: relative;
  width: 140px;
  height: 140px;
}

svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.gauge-track {
  fill: none;
  stroke: #e2e8f0;
  stroke-width: 10;
}

.gauge-fill {
  fill: none;
  stroke: #16a34a;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.6s ease;
}

.gauge.risk-medium .gauge-fill {
  stroke: #d97706;
}

.gauge.risk-high .gauge-fill {
  stroke: #dc2626;
}

.gauge-center {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
}

.gauge-center strong {
  font-size: 24px;
  line-height: 1.1;
}

.gauge-center span {
  color: #64748b;
  font-size: 12px;
  margin-top: 4px;
}
</style>
