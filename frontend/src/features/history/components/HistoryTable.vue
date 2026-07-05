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
        <span v-else class="thumb-empty">—</span>
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
  background: #fff;
  border: 1px solid #dbe3ec;
  border-radius: 12px;
  overflow: hidden;
}

.row {
  display: grid;
  grid-template-columns: 72px 1.4fr 100px 90px 100px 150px 90px;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eef2f6;
}

.row.head {
  background: #f1f5f9;
  font-size: 13px;
  font-weight: 700;
  color: #475569;
}

.row.body {
  cursor: pointer;
  transition: background 0.15s;
}

.row.body:hover {
  background: #f8fafc;
}

.row:last-child {
  border-bottom: 0;
}

.thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.thumb-empty {
  color: #94a3b8;
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
  background: #dcfce7;
  color: #15803d;
}

.label-tag.fake {
  background: #fee2e2;
  color: #b91c1c;
}

.time {
  font-size: 13px;
  color: #64748b;
}

.link-btn {
  height: 30px;
  padding: 0 10px;
  border: 0;
  border-radius: 6px;
  background: #eef2ff;
  color: #4338ca;
  cursor: pointer;
  font-size: 13px;
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
