<template>
  <section class="page asset-page">
    <PageHeader title="资产中心" description="管理已上传图片，快速从资产中心选择图片进行检测。">
      <template #actions>
        <BackHomeLink />
        <button class="primary-btn" :disabled="uploading" @click="pickFile">上传图片</button>
        <input ref="fileInput" type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" class="sr-only" @change="onFileChange" />
      </template>
    </PageHeader>

    <LoadingState :active="loading" message="加载资产列表..." />
    <InlineError :message="error" />

    <div class="asset-toolbar">
      <span>共 {{ total }} 张图片</span>
      <label>
        每页显示
        <select v-model.number="pageSize" @change="onPageSizeChange">
          <option v-for="size in pageSizeOptions" :key="size" :value="size">{{ size }} 张</option>
        </select>
      </label>
    </div>

    <div class="asset-grid">
      <div v-for="asset in assets" :key="asset.file_id" class="asset-card">
        <img v-if="asset.file_url" :src="resolveStorageUrl(asset.file_url)" alt="资产图片" />
        <div class="asset-body">
          <strong class="asset-name">{{ asset.original_filename }}</strong>
          <p class="asset-meta">{{ formatFileMeta(asset) }}</p>
          <div class="asset-actions">
            <button class="secondary-btn" @click="detectAsset(asset.file_id)">检测</button>
            <button class="danger-btn" :disabled="deletingId === asset.file_id" @click="removeAsset(asset)">
              {{ deletingId === asset.file_id ? '删除中' : '删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <EmptyState v-if="!loading && !assets.length" message="暂无已上传图片，可以先上传一张图片用于检测。">
      <template #action>
        <button @click="pickFile">上传图片</button>
      </template>
    </EmptyState>

    <Pagination
      v-model:page="page"
      :page-size="pageSize"
      :total="total"
      @update:page="load"
    />
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/shared/components/PageHeader.vue'
import BackHomeLink from '@/shared/components/BackHomeLink.vue'
import EmptyState from '@/shared/components/EmptyState.vue'
import LoadingState from '@/shared/components/LoadingState.vue'
import InlineError from '@/shared/components/InlineError.vue'
import Pagination from '@/shared/components/Pagination.vue'
import { uploadAsset, listAssets, deleteAsset } from '@/features/assets/services/asset.service'
import { routeNames } from '@/constants/routes'
import { resolveStorageUrl } from '@/utils/storage'
import { formatFileSize } from '@/utils/formatters'
import { useAsyncTask } from '@/composables/useAsyncTask'

const router = useRouter()
const { loading, error, run } = useAsyncTask()
const assets = ref([])
const page = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [6, 10, 20]
const total = ref(0)
const uploading = ref(false)
const fileInput = ref(null)
const deletingId = ref(null)

function formatFileMeta(asset) {
  return `${formatFileSize(asset.file_size)} · ${asset.file_type?.toUpperCase() || 'IMG'}`
}

async function load() {
  const data = await run(() => listAssets({ page: page.value, page_size: pageSize.value }), '加载资产中心失败。')
  if (data) {
    assets.value = data.items || []
    total.value = data.total || 0
  }
}

function pickFile() {
  fileInput.value?.click()
}

function onPageSizeChange() {
  page.value = 1
  load()
}

async function onFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const record = await uploadAsset(file)
    await load()
    const asset = record || null
    if (asset?.file_id) {
      router.push({ name: routeNames.detective, query: { asset: String(asset.file_id) } })
    }
  } catch (err) {
    error.value = '资产上传失败，请重试。'
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function detectAsset(fileId) {
  router.push({ name: routeNames.detective, query: { asset: String(fileId) } })
}

async function removeAsset(asset) {
  const filename = asset.original_filename || '该图片'
  if (!window.confirm(`确定删除“${filename}”吗？删除后资产中心将不再显示该图片。`)) {
    return
  }

  deletingId.value = asset.file_id
  try {
    await deleteAsset(asset.file_id)
    if (assets.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await load()
  } catch (err) {
    error.value = '删除资产失败，请重试。'
  } finally {
    deletingId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.page.asset-page {
  max-width: 1120px;
}

.asset-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid var(--line);
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(23, 32, 51, 0.05);
  color: var(--muted-strong);
  font-size: 14px;
  font-weight: 700;
}

.asset-toolbar label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.asset-toolbar select {
  height: 36px;
  min-width: 96px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  padding: 0 10px;
  background: #fff;
  color: var(--text);
  font: inherit;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
  margin-top: 0;
}

.asset-grid:empty {
  display: none;
}

.asset-card {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 16px 42px rgba(23, 32, 51, 0.07);
  display: grid;
  grid-template-rows: 180px 1fr;
}

.asset-card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background: var(--surface-soft);
}

.asset-body {
  display: grid;
  gap: 10px;
  padding: 18px;
}

.asset-name {
  margin: 0;
  font-size: 15px;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-meta {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.asset-actions {
  margin-top: auto;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.danger-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid rgba(180, 35, 24, 0.22);
  border-radius: 10px;
  background: rgba(180, 35, 24, 0.06);
  color: var(--danger);
  cursor: pointer;
  font-weight: 700;
}

.danger-btn:hover:not(:disabled) {
  background: rgba(180, 35, 24, 0.1);
}

@media (max-width: 640px) {
  .asset-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .asset-toolbar label {
    justify-content: space-between;
    width: 100%;
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
