<template>
  <section class="login-page">
    <form class="login-panel" @submit.prevent="submit">
      <div class="brand">
        <svg class="brand-icon" viewBox="0 0 32 32" aria-hidden="true">
          <path
            d="M16 4L4 26h24L16 4zm0 6.5l6.8 13.5H9.2L16 10.5z"
            fill="currentColor"
          />
        </svg>
        <h1>FaceShield</h1>
        <p>AI 换脸诈骗 · 伪造人脸检测系统</p>
      </div>
      <label>
        <span>用户名</span>
        <input v-model="username" autocomplete="username" placeholder="请输入用户名" />
      </label>
      <label>
        <span>密码</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="请输入密码"
        />
      </label>
      <InlineError :message="authStore.error" />
      <button :disabled="authStore.loading || !username || !password">
        {{ authStore.loading ? '登录中…' : '登录' }}
      </button>
      <p class="demo-hint">演示账号：demo / demo123456</p>
      <RouterLink class="back-link" to="/">返回首页</RouterLink>
    </form>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { login } from '@/features/auth/services/auth.service'
import InlineError from '@/shared/components/InlineError.vue'
import { authStore } from '@/stores/auth.store'
import { getApiErrorMessage } from '@/utils/api-response'

const router = useRouter()
const route = useRoute()
const username = ref('demo')
const password = ref('demo123456')

const redirectPath = computed(() => {
  const target = route.query.redirect
  return typeof target === 'string' && target.startsWith('/') ? target : '/detective'
})

async function submit() {
  authStore.setLoading(true)
  authStore.setError('')
  try {
    const data = await login(username.value, password.value)
    authStore.setSession(data.access_token, data.user)
    router.push(redirectPath.value)
  } catch (err) {
    authStore.setError(getApiErrorMessage(err, '登录失败，请检查用户名和密码。'))
  } finally {
    authStore.setLoading(false)
  }
}
</script>

<style scoped>
.brand {
  text-align: center;
  margin-bottom: 8px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  color: #166534;
  margin-bottom: 8px;
}

.brand h1 {
  margin: 0;
  font-size: 28px;
  letter-spacing: 0.04em;
}

.brand p {
  margin: 8px 0 0;
  color:rgb(52, 59, 68);
  font-size: 14px;
}

.demo-hint {
  margin: 0;
  text-align: center;
  color:rgb(53, 59, 68);
  font-size: 12px;
}

.back-link {
  display: block;
  text-align: center;
  color:rgb(64, 73, 86);
  font-size: 13px;
  text-decoration: none;
}

.back-link:hover {
  color: #166534;
}
</style>
