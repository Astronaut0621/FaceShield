export const appConfig = {
  name: 'FaceShield',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  storageBaseUrl: import.meta.env.VITE_STORAGE_BASE_URL || '',
  requestTimeoutMs: Number(import.meta.env.VITE_REQUEST_TIMEOUT_MS || 60000)
}
