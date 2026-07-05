import { reactive } from 'vue'

export const detectionStore = reactive({
  currentFile: null,
  latestResult: null,
  loading: false,
  error: '',
  setFile(file) {
    this.currentFile = file
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
    this.latestResult = null
    this.loading = false
    this.error = ''
  }
})

