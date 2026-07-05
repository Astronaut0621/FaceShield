<!-- Compatibility wrapper. New code should import from features/detection/components. -->
<template>
  <DetectionResultCard :result="result" />
</template>

<script setup>
import DetectionResultCard from '../features/detection/components/DetectionResultCard.vue'

defineProps({
  result: Object
})
</script>
