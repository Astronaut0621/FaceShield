import { reactive } from 'vue'

const TOKEN_KEY = 'faceshield_access_token'
const USER_KEY = 'faceshield_user'

function readJson(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || 'null')
  } catch {
    return null
  }
}

export const authStore = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: readJson(USER_KEY),
  loading: false,
  error: '',
  get isAuthenticated() {
    return Boolean(this.token)
  },
  setSession(token, user) {
    this.token = token
    this.user = user
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  clearSession() {
    this.token = ''
    this.user = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
  setLoading(value) {
    this.loading = value
  },
  setError(message) {
    this.error = message
  }
})

