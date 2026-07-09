<template>
  <section class="login-page">
    <form class="login-panel" @submit.prevent="submit">
      <div class="brand">
        <img class="brand-mark" src="/images/logo.png" alt="" aria-hidden="true" />
        <h1>FaceShield</h1>
        <p>AI 换脸伪造检测系统</p>
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
        {{ authStore.loading ? '登录中...' : '登录' }}
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
  display: grid;
  justify-items: center;
  gap: 8px;
  text-align: center;
  margin-bottom: 6px;
}

.brand-mark {
  width: 66px;
  height: 66px;
  display: block;
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 50%;
  background: #fff;
  object-fit: cover;
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.18);
}

.brand h1 {
  margin: 0;
  font-size: 30px;
  letter-spacing: -0.02em;
}

.brand p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
}

.demo-hint {
  margin: 0;
  text-align: center;
  color: var(--muted);
  font-size: 12px;
}

.back-link {
  display: block;
  text-align: center;
  color: var(--muted-strong);
  font-size: 13px;
  font-weight: 650;
  text-decoration: none;
}

.back-link:hover {
  color: var(--accent);
}
</style>
