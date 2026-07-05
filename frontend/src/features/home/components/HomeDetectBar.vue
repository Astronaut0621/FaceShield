<template>
  <div class="detect-bar">
    <div class="detect-field">
      <span class="field-label">检测模式</span>
      <span class="field-value">频域 + 空域融合</span>
    </div>
    <div class="divider" />
    <div class="detect-field">
      <span class="field-label">支持格式</span>
      <span class="field-value">JPG / PNG</span>
    </div>
    <div class="divider" />
    <div class="detect-field">
      <span class="field-label">输出结果</span>
      <span class="field-value">概率 · 风险 · 热力图</span>
    </div>
    <div class="divider" />
    <div class="detect-field">
      <span class="field-label">适用场景</span>
      <span class="field-value">AI 换脸诈骗识别</span>
    </div>
  </div>
</template>

<style scoped>
.detect-bar {
  display: flex;
  align-items: center;
  gap: 0;
  width: min(920px, calc(100% - 48px));
  margin: 0 auto;
  padding: 20px 24px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.12);
}

.detect-field {
  flex: 1;
  display: grid;
  gap: 6px;
  padding: 0 20px;
  min-width: 0;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
}

.field-value {
  font-size: 14px;
  font-weight: 500;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.divider {
  width: 1px;
  height: 44px;
  background: #e2e8f0;
  flex-shrink: 0;
}

.search-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 52px;
  padding: 0 28px;
  margin-left: 12px;
  border-radius: 12px;
  background: #166534;
  color: #fff;
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  transition: background 0.15s;
}

.search-btn svg {
  width: 20px;
  height: 20px;
}

.search-btn:hover {
  background: #15803d;
}

@media (max-width: 860px) {
  .detect-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 20px;
  }

  .divider {
    width: 100%;
    height: 1px;
  }

  .detect-field {
    padding: 0;
  }

  .search-btn {
    margin-left: 0;
    justify-content: center;
  }
}
</style>
