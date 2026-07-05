import { http } from '../../../services/http'
import { unwrapApiResponse } from '../../../utils/api-response'

export async function uploadAndDetect(file) {
  const form = new FormData()
  form.append('file', file)
  const response = await http.post('/detect', form)
  return unwrapApiResponse(response)
}

export async function startDetection(fileId) {
  const response = await http.post('/detection/start', { file_id: fileId })
  return unwrapApiResponse(response)
}
