<template>
  <RouterView v-if="route.meta.standalone" />
  <AppLayout v-else>
    <RouterView />
  </AppLayout>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppLayout from './layouts/AppLayout.vue'

const route = useRoute()
</script>
