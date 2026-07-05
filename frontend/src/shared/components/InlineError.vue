<template>
  <p v-if="message" class="error">{{ message }}</p>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  }
})
</script>

