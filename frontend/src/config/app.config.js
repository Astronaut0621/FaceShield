export const appConfig = {
  name: 'FaceShield',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  storageBaseUrl: import.meta.env.VITE_STORAGE_BASE_URL || 'http://localhost:8000'
}
