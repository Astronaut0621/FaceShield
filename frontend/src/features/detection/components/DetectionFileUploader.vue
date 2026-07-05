<template>
  <section class="panel">
    <label class="drop-zone">
      <input type="file" accept=".jpg,.jpeg,.png,.bmp" @change="onChange" />
      <span>{{ filename || 'Choose an image' }}</span>
    </label>
    <img v-if="previewUrl" class="preview" :src="previewUrl" alt="Selected image preview" />
    <button :disabled="!modelValue || loading" @click="$emit('submit')">
      {{ loading ? 'Detecting...' : 'Start Detection' }}
    </button>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: File,
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'submit'])
const filename = ref('')
const previewUrl = ref('')

function onChange(event) {
  const file = event.target.files?.[0]
  emit('update:modelValue', file || null)
  filename.value = file?.name || ''
  previewUrl.value = file ? URL.createObjectURL(file) : ''
}
</script>

