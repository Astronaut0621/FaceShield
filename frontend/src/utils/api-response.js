export function unwrapApiResponse(response) {
  const payload = response.data
  if (!payload || typeof payload !== 'object') return null
  if (payload.code !== undefined && payload.code !== 200) {
    const error = new Error(payload.message || 'Request failed.')
    error.response = response
    throw error
  }
  return payload.data ?? null
}

export function getApiErrorMessage(error, fallback = 'Request failed.') {
  return error.response?.data?.message || error.message || fallback
}
