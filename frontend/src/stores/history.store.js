import { reactive } from 'vue'

export const historyStore = reactive({
  items: [],
  total: 0,
  loading: false,
  error: '',
  setList(payload) {
    this.items = payload?.items || []
    this.total = payload?.total || 0
  },
  setLoading(value) {
    this.loading = value
  },
  setError(message) {
    this.error = message
  }
})

