<template>
  <div class="history-table">
    <div class="row head">
      <span>缩略图</span>
      <span>文件名</span>
      <span>结论</span>
      <span>伪造概率</span>
      <span>风险等级</span>
      <span>检测时间</span>
      <span>操作</span>
    </div>
    <div
      v-for="item in items"
      :key="item.taskId"
      class="row body"
      @click="goDetail(item.taskId)"
    >
      <span class="thumb-cell">
        <img
          v-if="item.originalImageUrl"
          :src="resolveStorageUrl(item.originalImageUrl)"
          alt=""
          class="thumb"
        />
        <span v-else class="thumb-empty">无图</span>
      </span>
      <span class="filename" :title="item.originalFilename">{{ item.originalFilename || '-' }}</span>
      <span>
        <span :class="['label-tag', item.label]">{{ formatLabel(item.label) }}</span>
      </span>
      <span>{{ formatPercent(item.fakeProbability, 1) }}</span>
      <span><RiskBadge :level="item.riskLevel" /></span>
      <span class="time">{{ formatDateTime(item.createdAt) }}</span>
      <span>
        <button class="link-btn" @click.stop="goDetail(item.taskId)">查看详情</button>
      </span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import RiskBadge from '@/features/detection/components/result/RiskBadge.vue'
import { routeNames } from '@/constants/routes'
import { formatDateTime, formatLabel, formatPercent } from '@/utils/formatters'
import { resolveStorageUrl } from '@/utils/storage'

defineProps({
  items: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()

function goDetail(taskId) {
  if (!taskId) return
  router.push({ name: routeNames.historyDetail, params: { id: taskId } })
}
</script>

<style scoped>
.history-table {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 16px 42px rgba(23, 32, 51, 0.07);
}

.row {
  display: grid;
  grid-template-columns: 72px 1.4fr 100px 90px 100px 150px 90px;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
}

.row.head {
  background: var(--surface-soft);
  font-size: 13px;
  font-weight: 700;
  color: var(--muted-strong);
}

.row.body {
  cursor: pointer;
  transition: background 0.15s;
}

.row.body:hover {
  background: var(--surface-soft);
}

.row:last-child {
  border-bottom: 0;
}

.thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid var(--line);
}

.thumb-empty {
  color: #9caeaa;
}

.filename {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.label-tag {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.label-tag.real {
  background: var(--accent-soft);
  color: var(--accent);
}

.label-tag.fake {
  background: #fee2e2;
  color: #b42318;
}

.time {
  font-size: 13px;
  color: var(--muted);
}

.link-btn {
  height: 30px;
  padding: 0 10px;
  border: 0;
  border-radius: 9px;
  background: var(--accent-soft);
  color: var(--accent);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.link-btn:hover {
  background: var(--accent);
  color: #fff;
  box-shadow: none;
}

@media (max-width: 960px) {
  .row {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .row.head {
    display: none;
  }

  .row.body {
    padding: 16px;
  }
}
</style>
