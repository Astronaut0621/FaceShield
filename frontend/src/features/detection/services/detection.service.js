import { http } from '../../../services/http'
import { unwrapApiResponse } from '../../../utils/api-response'
import { normalizeDetectionResult } from '../../../utils/detection'

export async function uploadAndDetect(file) {
  const form = new FormData()
  form.append('file', file)
  const response = await http.post('/detection/upload-and-detect', form)
  return normalizeDetectionResult(unwrapApiResponse(response))
}

export async function getDetectionDetail(taskId) {
  const response = await http.get(`/records/${taskId}`)
  return normalizeDetectionResult(unwrapApiResponse(response))
}

export async function startDetection(fileId) {
  const response = await http.post('/detection/start', { file_id: fileId })
  return normalizeDetectionResult(unwrapApiResponse(response))
}
