<template>
  <section class="uploader" :class="{ large }">
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
        <div class="drop-icon">📤</div>
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
        {{ loading ? '检测中，请稍候…' : '开始检测' }}
      </button>
      <p class="hint">系统将融合频域与空域特征，分析是否存在 AI 换脸伪造痕迹</p>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: File,
  loading: Boolean,
  large: Boolean
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
  min-height: 300px;
  border: 2px dashed #94a3b8;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}

.drop-zone.active {
  border-color: #2563eb;
  background: linear-gradient(180deg, #eff6ff 0%, #f0f9ff 100%);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.drop-zone.disabled {
  opacity: 0.7;
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
  gap: 8px;
  padding: 32px 24px;
  text-align: center;
}

.drop-icon {
  font-size: 36px;
}

.drop-content p {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.drop-content span {
  color: #64748b;
  font-size: 13px;
}

.preview {
  max-width: min(100%, 420px);
  max-height: 280px;
  border-radius: 10px;
  object-fit: contain;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}

.preview-meta {
  display: grid;
  gap: 4px;
}

.preview-meta span {
  color: #64748b;
  font-size: 13px;
}

.ghost-btn {
  position: relative;
  z-index: 2;
  height: 34px;
  padding: 0 14px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  cursor: pointer;
}

.uploader-actions {
  display: grid;
  gap: 8px;
  justify-items: center;
  text-align: center;
}

.uploader.large .drop-zone {
  min-height: 380px;
}

.uploader.large .drop-content {
  padding: 48px 32px;
}

.uploader.large .drop-icon {
  font-size: 48px;
}

.uploader.large .drop-content p {
  font-size: 18px;
}

.uploader.large .preview {
  max-width: min(100%, 560px);
  max-height: 360px;
}

.uploader.large .primary-btn {
  width: 100%;
  max-width: 320px;
  height: 50px;
  font-size: 16px;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 44px;
  border: 0;
  border-radius: 8px;
  background: linear-gradient(135deg, #166534, #15803d);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  width: fit-content;
  min-width: 160px;
  padding: 0 24px;
}

.primary-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.hint {
  margin: 0;
  color: #64748b;
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
</style>
