<template>
  <aside class="guide-panel" aria-label="检测说明">
    <section class="guide-block">
      <h3>检测流程</h3>
      <ol class="steps">
        <li v-for="(step, index) in steps" :key="step.title">
          <span class="step-num">{{ index + 1 }}</span>
          <div>
            <strong>{{ step.title }}</strong>
            <p>{{ step.desc }}</p>
          </div>
        </li>
      </ol>
    </section>

    <section class="guide-block">
      <h3>融合分析</h3>
      <div class="tech-cards">
        <article v-for="item in techItems" :key="item.title" class="tech-card">
          <span class="tech-icon">{{ item.code }}</span>
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.desc }}</p>
          </div>
        </article>
      </div>
    </section>

    <section class="guide-block tips">
      <h3>使用提示</h3>
      <ul>
        <li>上传清晰、正面的人脸照片，检测效果更稳定</li>
        <li>支持 JPG、JPEG、PNG，单张图片检测</li>
        <li>检测完成后可查看概率、风险等级与热力图</li>
      </ul>
    </section>
  </aside>
</template>

<script setup>
const steps = [
  { title: '上传图片', desc: '拖拽或选择待检测人脸图片' },
  { title: '选择模型', desc: '使用默认模型，或指定可用检测模型' },
  { title: '融合推理', desc: '频域 FFT 与空域 CNN 共同判断' },
  { title: '结果可视化', desc: '输出风险等级与可疑区域热力图' }
]

const techItems = [
  { code: 'FFT', title: '频域分支', desc: '幅度谱捕捉高频伪影与压缩残留' },
  { code: 'CNN', title: '空域分支', desc: '纹理分析识别换脸边界痕迹' },
  { code: 'CAM', title: '热力图', desc: '高亮模型关注区域' }
]
</script>

<style scoped>
.guide-panel {
  display: grid;
  gap: 14px;
}

.guide-block {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 14px 34px rgba(23, 32, 51, 0.05);
}

.guide-block h3 {
  margin: 0 0 16px;
  font-size: 15px;
  color: var(--text);
}

.steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 14px;
}

.steps li {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-num {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 13px;
  font-weight: 900;
}

.steps strong {
  display: block;
  font-size: 14px;
  color: var(--text);
  margin-bottom: 2px;
}

.steps p {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

.tech-cards {
  display: grid;
  gap: 10px;
}

.tech-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 14px;
  background: var(--surface-soft);
  border: 1px solid var(--line);
}

.tech-icon {
  width: 42px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: var(--text);
  color: var(--accent-glow);
  font-size: 11px;
  font-weight: 900;
  flex-shrink: 0;
}

.tech-card strong {
  display: block;
  font-size: 13px;
  color: var(--text);
  margin-bottom: 2px;
}

.tech-card p {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.5;
}

.tips ul {
  margin: 0;
  padding-left: 18px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.85;
}
</style>
