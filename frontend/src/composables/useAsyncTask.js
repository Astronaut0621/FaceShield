import { ref } from 'vue'
import { getApiErrorMessage } from '../utils/api-response'

export function useAsyncTask() {
  const loading = ref(false)
  const error = ref('')

  async function run(task, fallbackMessage) {
    loading.value = true
    error.value = ''
    try {
      return await task()
    } catch (err) {
      error.value = getApiErrorMessage(err, fallbackMessage)
      return null
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run }
}

