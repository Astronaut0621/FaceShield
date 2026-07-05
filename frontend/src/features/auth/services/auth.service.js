import { http } from '../../../services/http'
import { unwrapApiResponse } from '../../../utils/api-response'

export async function login(username, password) {
  const response = await http.post('/auth/login', { username, password })
  return unwrapApiResponse(response)
}

export async function logout() {
  const response = await http.post('/auth/logout')
  return unwrapApiResponse(response)
}

export async function getCurrentUser() {
  const response = await http.get('/auth/me')
  return unwrapApiResponse(response)
}

