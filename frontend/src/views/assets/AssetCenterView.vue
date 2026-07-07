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

    <div class="asset-grid">
      <div v-for="asset in assets" :key="asset.file_id" class="asset-card">
        <img v-if="asset.file_url" :src="resolveStorageUrl(asset.file_url)" alt="资产图片" />
        <div class="asset-body">
          <strong class="asset-name">{{ asset.original_filename }}</strong>
          <p class="asset-meta">{{ formatFileMeta(asset) }}</p>
          <div class="asset-actions">
            <button class="secondary-btn" @click="detectAsset(asset.file_id)">检测</button>
          </div>
        </div>
      </div>
    </div>

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
import LoadingState from '@/shared/components/LoadingState.vue'
import InlineError from '@/shared/components/InlineError.vue'
import Pagination from '@/shared/components/Pagination.vue'
import { uploadAsset, listAssets } from '@/features/assets/services/asset.service'
import { routeNames } from '@/constants/routes'
import { resolveStorageUrl } from '@/utils/storage'
import { formatFileSize } from '@/utils/formatters'
import { useAsyncTask } from '@/composables/useAsyncTask'

const router = useRouter()
const { loading, error, run } = useAsyncTask()
const assets = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const uploading = ref(false)
const fileInput = ref(null)

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

onMounted(load)
</script>

<style scoped>
.page.asset-page {
  max-width: 1120px;
}

.asset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
  margin-top: 20px;
}

.asset-card {
  background: #fff;
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
  background: #f8fafc;
}

.asset-body {
  display: grid;
  gap: 10px;
  padding: 18px;
}

.asset-name {
  margin: 0;
  font-size: 15px;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-meta {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.asset-actions {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
}

.secondary-btn {
  min-width: 100px;
  height: 38px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
  color: #334155;
  cursor: pointer;
}

.secondary-btn:hover {
  background: #eef2ff;
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
