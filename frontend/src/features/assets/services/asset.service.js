import { http } from '@/services/http'
import { unwrapApiResponse } from '@/utils/api-response'

export async function uploadAsset(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await http.post('/assets/upload', formData)
  return unwrapApiResponse(response)
}

export async function listAssets(params = {}) {
  const response = await http.get('/assets/list', { params })
  return unwrapApiResponse(response)
}

export async function getAsset(fileId) {
  const response = await http.get(`/assets/${fileId}`)
  return unwrapApiResponse(response)
}
