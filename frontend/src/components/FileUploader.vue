<!-- Compatibility wrapper. New code should import from features/detection/components. -->
<template>
  <DetectionFileUploader v-bind="$props" @update:modelValue="$emit('update:modelValue', $event)" @submit="$emit('submit')" />
</template>

<script setup>
import DetectionFileUploader from '../features/detection/components/DetectionFileUploader.vue'

defineProps({
  modelValue: File,
  loading: Boolean
})

defineEmits(['update:modelValue', 'submit'])
</script>
