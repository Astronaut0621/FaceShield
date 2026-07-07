import { appConfig } from '../config/app.config'

export function resolveStorageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) return path
  if (path.startsWith('data:') || path.startsWith('blob:')) return path
  const base = appConfig.storageBaseUrl.replace(/\/$/, '')
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${base}${normalized}`
}
