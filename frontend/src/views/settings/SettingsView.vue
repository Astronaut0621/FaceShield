<template>
  <section class="page settings-page">
    <PageHeader title="设置" description="查看当前账号、接口地址和前端运行配置。" />

    <div class="settings-grid">
      <article class="settings-card">
        <span class="card-kicker">账号</span>
        <h3>{{ displayName }}</h3>
        <dl>
          <div>
            <dt>用户名</dt>
            <dd>{{ authStore.user?.username || '-' }}</dd>
          </div>
          <div>
            <dt>登录状态</dt>
            <dd>已登录</dd>
          </div>
        </dl>
      </article>

      <article class="settings-card">
        <span class="card-kicker">系统</span>
        <h3>{{ appConfig.name }}</h3>
        <dl>
          <div>
            <dt>API 地址</dt>
            <dd>{{ appConfig.apiBaseUrl }}</dd>
          </div>
          <div>
            <dt>存储地址</dt>
            <dd>{{ appConfig.storageBaseUrl || '同源地址' }}</dd>
          </div>
        </dl>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import PageHeader from '@/shared/components/PageHeader.vue'
import { appConfig } from '@/config/app.config'
import { authStore } from '@/stores/auth.store'

const displayName = computed(() => authStore.user?.display_name || authStore.user?.username || '当前用户')
</script>

<style scoped>
.settings-page {
  max-width: 1120px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.settings-card {
  display: grid;
  gap: 18px;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 16px 42px rgba(23, 32, 51, 0.07);
}

.card-kicker {
  width: fit-content;
  padding: 5px 10px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 12px;
  font-weight: 800;
}

.settings-card h3 {
  margin: 0;
  color: var(--text);
  font-size: 22px;
}

.settings-card dl {
  display: grid;
  gap: 12px;
  margin: 0;
}

.settings-card dl div {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
}

.settings-card dt {
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}

.settings-card dd {
  min-width: 0;
  margin: 0;
  color: var(--muted-strong);
  word-break: break-all;
}

@media (max-width: 760px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }

  .settings-card dl div {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
