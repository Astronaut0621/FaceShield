<template>
  <header class="page-header">
    <div>
      <h2>{{ title }}</h2>
      <p v-if="description">{{ description }}</p>
    </div>
    <slot name="actions" />
  </header>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})
</script>

