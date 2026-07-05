<template>
  <div class="table">
    <div class="row head">
      <span>Task</span>
      <span>Filename</span>
      <span>Label</span>
      <span>Risk</span>
      <span>Probability</span>
    </div>
    <div v-for="item in items" :key="item.task_id" class="row">
      <span>#{{ item.task_id }}</span>
      <span>{{ item.original_filename }}</span>
      <span>{{ item.label || '-' }}</span>
      <span>{{ item.risk_level || '-' }}</span>
      <span>{{ formatPercent(item.fake_probability) }}</span>
    </div>
  </div>
</template>

<script setup>
import { formatPercent } from '../../../utils/formatters'

defineProps({
  items: {
    type: Array,
    default: () => []
  }
})
</script>
