import axios from 'axios'
import { appConfig } from '../config/app.config'
import { authStore } from '../stores/auth.store'

export const http = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 30000
})

http.interceptors.response.use(
  response => response,
  error => Promise.reject(error)
)

http.interceptors.request.use(config => {
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }
  return config
})
