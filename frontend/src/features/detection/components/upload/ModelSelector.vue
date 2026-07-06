<template>
  <div class="model-selector">
    <label class="selector-label" for="model-select">检测模型</label>
    <div class="selector-row">
      <select
        id="model-select"
        :value="modelValue"
        :disabled="disabled || loading"
        @change="onChange"
      >
        <option v-if="loading" value="">加载模型列表...</option>
        <option v-else-if="!options.length" value="">暂无可用模型</option>
        <option v-for="item in options" :key="item.id" :value="item.id">
          {{ formatOption(item) }}
        </option>
      </select>
      <span v-if="selected?.isActive" class="active-tag">默认</span>
    </div>
    <p v-if="selected?.description" class="model-desc">{{ selected.description }}</p>
    <InlineError v-if="error" :message="error" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import InlineError from '@/shared/components/InlineError.vue'
import { listModels } from '@/features/detection/services/model.service'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: ''
  },
  disabled: Boolean
})

const emit = defineEmits(['update:modelValue'])

const options = ref([])
const loading = ref(false)
const error = ref('')

const selected = computed(() =>
  options.value.find(item => Number(item.id) === Number(props.modelValue))
)

function formatOption(item) {
  const active = item.isActive ? '（当前默认）' : ''
  return `${item.modelName} / ${item.version}${active}`
}

function onChange(event) {
  const value = event.target.value
  emit('update:modelValue', value ? Number(value) : '')
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    options.value = await listModels()
    if (!props.modelValue && options.value.length) {
      const active = options.value.find(item => item.isActive) || options.value[0]
      emit('update:modelValue', active.id)
    }
  } catch (err) {
    error.value = '模型列表加载失败'
    options.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.model-selector {
  display: grid;
  gap: 8px;
  margin-bottom: 20px;
}

.selector-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--muted-strong);
}

.selector-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

select {
  flex: 1;
  height: 44px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  padding: 0 14px;
  background: var(--surface);
  font: inherit;
  color: var(--text);
  cursor: pointer;
}

select:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

select:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.active-tag {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 12px;
  font-weight: 750;
}

.model-desc {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}
</style>
