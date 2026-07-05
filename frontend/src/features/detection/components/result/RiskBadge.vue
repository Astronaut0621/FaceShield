<template>
  <span class="risk-badge" :class="riskLevelClass(level)">
    {{ formatRiskLevel(level) }}
  </span>
</template>

<script setup>
import { formatRiskLevel, riskLevelClass } from '@/utils/formatters'

defineProps({
  level: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.risk-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.risk-badge.risk-low {
  background: #dcfce7;
  color: #15803d;
}

.risk-badge.risk-medium {
  background: #fef3c7;
  color: #b45309;
}

.risk-badge.risk-high {
  background: #fee2e2;
  color: #b91c1c;
}
</style>
