import { http } from '@/services/http'
import { unwrapApiResponse } from '@/utils/api-response'

export function normalizeModelOption(raw) {
  if (!raw) return null
  return {
    id: raw.id,
    modelName: raw.model_name,
    version: raw.version,
    description: raw.description ?? '',
    isActive: Boolean(raw.is_active)
  }
}

export async function listModels() {
  const response = await http.get('/model-version/list')
  const data = unwrapApiResponse(response)
  return (data || []).map(normalizeModelOption)
}

export async function getActiveModel() {
  const response = await http.get('/model-version')
  return normalizeModelOption(unwrapApiResponse(response))
}
