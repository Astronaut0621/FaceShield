<template>
  <section class="login-page">
    <form class="login-panel" @submit.prevent="submit">
      <h1>FaceShield</h1>
      <label>
        <span>Username</span>
        <input v-model="username" autocomplete="username" />
      </label>
      <label>
        <span>Password</span>
        <input v-model="password" type="password" autocomplete="current-password" />
      </label>
      <InlineError :message="authStore.error" />
      <button :disabled="authStore.loading || !username || !password">
        {{ authStore.loading ? 'Signing in...' : 'Sign in' }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../features/auth/services/auth.service'
import InlineError from '../shared/components/InlineError.vue'
import { authStore } from '../stores/auth.store'
import { getApiErrorMessage } from '../utils/api-response'

const router = useRouter()
const username = ref('demo')
const password = ref('demo123456')

async function submit() {
  authStore.setLoading(true)
  authStore.setError('')
  try {
    const data = await login(username.value, password.value)
    authStore.setSession(data.access_token, data.user)
    router.push('/')
  } catch (err) {
    authStore.setError(getApiErrorMessage(err, 'Login failed.'))
  } finally {
    authStore.setLoading(false)
  }
}
</script>

