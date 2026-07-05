import axios from 'axios'
import { appConfig } from '../config/app.config'
import { authStore } from '../stores/auth.store'

export const http = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 60000
})

http.interceptors.request.use(config => {
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})

http.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      authStore.clearSession()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
