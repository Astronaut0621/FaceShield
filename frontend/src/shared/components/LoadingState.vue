<template>
  <p v-if="active" class="muted">{{ message }}</p>
</template>

<script setup>
defineProps({
  active: Boolean,
  message: {
    type: String,
    default: 'Loading...'
  }
})
</script>

