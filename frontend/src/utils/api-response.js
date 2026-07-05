export function unwrapApiResponse(response) {
  return response.data?.data ?? null
}

export function getApiErrorMessage(error, fallback = 'Request failed.') {
  return error.response?.data?.message || error.message || fallback
}

