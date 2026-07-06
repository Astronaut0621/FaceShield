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
      <span class="field-value">概率 / 风险 / 热力图</span>
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
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  align-items: stretch;
  width: min(1000px, calc(100% - 48px));
  margin: 0 auto;
  padding: 8px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(216, 228, 222, 0.92);
  border-radius: 18px;
  box-shadow: 0 18px 55px rgba(16, 35, 27, 0.14);
}

.detect-field {
  display: grid;
  gap: 5px;
  padding: 15px 18px;
  min-width: 0;
}

.field-label {
  font-size: 12px;
  font-weight: 750;
  color: #60756b;
}

.field-value {
  font-size: 14px;
  font-weight: 750;
  color: #10231b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.divider {
  width: 1px;
  height: 48px;
  align-self: center;
  margin-left: -1px;
  background: #d8e4de;
}

@media (max-width: 860px) {
  .detect-bar {
    grid-template-columns: 1fr 1fr;
    width: calc(100% - 28px);
  }

  .divider {
    display: none;
  }
}

@media (max-width: 560px) {
  .detect-bar {
    grid-template-columns: 1fr;
  }
}
</style>
