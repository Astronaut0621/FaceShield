import { http } from '../../../services/http'
import { unwrapApiResponse } from '../../../utils/api-response'

export async function listHistory(params = {}) {
  const response = await http.get('/records', { params })
  return unwrapApiResponse(response)
}

export async function getHistoryDetail(taskId) {
  const response = await http.get(`/records/${taskId}`)
  return unwrapApiResponse(response)
}
