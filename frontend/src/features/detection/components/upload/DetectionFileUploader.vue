<template>
  <section class="uploader">
    <div
      class="drop-zone"
      :class="{ active: dragging, disabled: loading, 'has-file': previewUrl }"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        :disabled="loading"
        @change="onChange"
      />
      <div v-if="!previewUrl" class="drop-content">
        <div class="drop-icon">IMG</div>
        <p>拖拽图片到此处，或点击选择文件</p>
        <span>支持 JPG / JPEG / PNG，单张图片检测</span>
      </div>
      <div v-else class="preview-wrap">
        <img class="preview" :src="previewUrl" alt="待检测图片预览" />
        <div class="preview-meta">
          <strong>{{ filename }}</strong>
          <span>{{ fileSizeText }}</span>
        </div>
        <button type="button" class="ghost-btn" :disabled="loading" @click.stop="clearFile">
          重新选择
        </button>
      </div>
    </div>

    <div class="uploader-actions">
      <button class="primary-btn" :disabled="!modelValue || loading" @click="$emit('submit')">
        <span v-if="loading" class="spinner" />
        {{ loading ? '检测中，请稍候...' : '开始检测' }}
      </button>
      <p class="hint">系统将融合频域与空域特征，分析是否存在 AI 换脸伪造痕迹。</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: File,
  loading: Boolean
})

const emit = defineEmits(['update:modelValue', 'submit'])

const fileInput = ref(null)
const filename = ref('')
const previewUrl = ref('')
const dragging = ref(false)

const fileSizeText = computed(() => {
  if (!props.modelValue) return ''
  const size = props.modelValue.size
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(2)} MB`
})

watch(
  () => props.modelValue,
  file => {
    if (!file) {
      filename.value = ''
      previewUrl.value = ''
    }
  }
)

function acceptFile(file) {
  if (!file) return
  const allowed = ['image/jpeg', 'image/png']
  const ext = file.name.split('.').pop()?.toLowerCase()
  const validExt = ['jpg', 'jpeg', 'png'].includes(ext)
  if (!allowed.includes(file.type) && !validExt) {
    alert('仅支持 JPG、JPEG、PNG 格式图片')
    return
  }
  emit('update:modelValue', file)
  filename.value = file.name
  previewUrl.value = URL.createObjectURL(file)
}

function onChange(event) {
  acceptFile(event.target.files?.[0])
}

function onDrop(event) {
  dragging.value = false
  acceptFile(event.dataTransfer.files?.[0])
}

function clearFile() {
  emit('update:modelValue', null)
  filename.value = ''
  previewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<style scoped>
.uploader {
  display: grid;
  gap: 16px;
}

.drop-zone {
  position: relative;
  min-height: 330px;
  display: grid;
  place-items: center;
  border: 1.5px dashed #9fb8ad;
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(246, 250, 248, 0.9), rgba(255, 255, 255, 0.96)),
    #fff;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.drop-zone.active {
  border-color: #087443;
  background: #e1f4eb;
  box-shadow: 0 0 0 5px rgba(8, 116, 67, 0.1);
  transform: translateY(-1px);
}

.drop-zone.has-file {
  border-style: solid;
  background: #f6faf8;
}

.drop-zone.disabled {
  opacity: 0.72;
  pointer-events: none;
}

.drop-zone input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.drop-content,
.preview-wrap {
  display: grid;
  place-items: center;
  gap: 10px;
  width: 100%;
  padding: 34px 24px;
  text-align: center;
}

.drop-icon {
  width: 62px;
  height: 62px;
  display: grid;
  place-items: center;
  border-radius: 18px;
  background: #e1f4eb;
  color: #065f36;
  font-size: 13px;
  font-weight: 900;
}

.drop-content p {
  margin: 8px 0 0;
  font-size: 17px;
  font-weight: 800;
  color: #10231b;
}

.drop-content span {
  color: #60756b;
  font-size: 13px;
}

.preview {
  max-width: min(100%, 460px);
  max-height: 300px;
  border-radius: 16px;
  object-fit: contain;
  background: #10231b;
  box-shadow: 0 16px 44px rgba(16, 35, 27, 0.16);
}

.preview-meta {
  display: grid;
  gap: 4px;
  max-width: 100%;
}

.preview-meta strong {
  overflow-wrap: anywhere;
}

.preview-meta span {
  color: #60756b;
  font-size: 13px;
}

.ghost-btn {
  position: relative;
  z-index: 2;
  min-height: 36px;
  padding: 0 14px;
  border: 1px solid #bfd0c7;
  background: #fff;
  color: #33463d;
}

.ghost-btn:hover:not(:disabled) {
  background: #f6faf8;
  color: #087443;
  box-shadow: none;
}

.uploader-actions {
  display: grid;
  gap: 8px;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 46px;
  width: fit-content;
  min-width: 168px;
  padding: 0 24px;
  font-size: 15px;
  font-weight: 800;
}

.hint {
  margin: 0;
  color: #60756b;
  font-size: 13px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 560px) {
  .primary-btn {
    width: 100%;
  }
}
</style>
