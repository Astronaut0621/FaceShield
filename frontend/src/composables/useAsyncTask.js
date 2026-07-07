import { ref } from 'vue'
import { getApiErrorMessage } from '../utils/api-response'

export function useAsyncTask() {
  const loading = ref(false)
  const error = ref('')
  let currentRunId = 0

  async function run(task, fallbackMessage) {
    const runId = ++currentRunId
    loading.value = true
    error.value = ''
    try {
      return await task()
    } catch (err) {
      if (runId === currentRunId) {
        error.value = getApiErrorMessage(err, fallbackMessage)
      }
      return null
    } finally {
      if (runId === currentRunId) {
        loading.value = false
      }
    }
  }

  return { loading, error, run }
}
