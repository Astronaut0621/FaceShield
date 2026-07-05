<template>
  <p class="empty">{{ message }}</p>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'No data.'
  }
})
</script>

