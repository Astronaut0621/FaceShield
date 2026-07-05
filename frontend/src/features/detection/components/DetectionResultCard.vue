<template>
  <section v-if="result" class="panel result-panel">
    <div>
      <span class="label">Label</span>
      <strong>{{ result.label || '-' }}</strong>
    </div>
    <div>
      <span class="label">Fake probability</span>
      <strong>{{ formatPercent(result.fake_probability) }}</strong>
    </div>
    <div>
      <span class="label">Risk level</span>
      <strong :class="['risk', result.risk_level]">{{ result.risk_level || '-' }}</strong>
    </div>
    <div>
      <span class="label">Frequency score</span>
      <strong>{{ formatPercent(result.frequency_score) }}</strong>
    </div>
    <div>
      <span class="label">Spatial score</span>
      <strong>{{ formatPercent(result.spatial_score) }}</strong>
    </div>
    <p>{{ result.suggestion }}</p>
  </section>
</template>

<script setup>
import { formatPercent } from '../../../utils/formatters'

defineProps({
  result: Object
})
</script>

