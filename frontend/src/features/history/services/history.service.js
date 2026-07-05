import { http } from '../../../services/http'
import { unwrapApiResponse } from '../../../utils/api-response'
import { normalizeDetectionResult } from '../../../utils/detection'

function mapListResponse(data) {
  return {
    total: data.total ?? 0,
    items: (data.items || []).map(item =>
      normalizeDetectionResult({
        ...item,
        original_image_url: item.original_image_url
      })
    )
  }
}

export async function listHistory(params = {}) {
  const hasFilters = params.label || params.risk_level
  const endpoint = hasFilters ? '/history/list' : '/records'
  const response = await http.get(endpoint, { params })
  return mapListResponse(unwrapApiResponse(response))
}

export async function getHistoryDetail(taskId) {
  const response = await http.get(`/records/${taskId}`)
  return normalizeDetectionResult(unwrapApiResponse(response))
}
