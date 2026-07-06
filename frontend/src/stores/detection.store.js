import { reactive } from 'vue'

export const detectionStore = reactive({
  currentFile: null,
  selectedModelId: null,
  latestResult: null,
  loading: false,
  error: '',
  setFile(file) {
    this.currentFile = file
  },
  setSelectedModelId(modelId) {
    this.selectedModelId = modelId
  },
  setResult(result) {
    this.latestResult = result
  },
  setLoading(value) {
    this.loading = value
  },
  setError(message) {
    this.error = message
  },
  reset() {
    this.currentFile = null
    this.selectedModelId = null
    this.latestResult = null
    this.loading = false
    this.error = ''
  }
})

