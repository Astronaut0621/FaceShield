<template>
  <aside class="guide-panel">
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
          <span class="tech-icon">{{ item.icon }}</span>
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
        <li>请上传清晰、正面的人脸照片，效果更佳</li>
        <li>支持 JPG / JPEG / PNG，单张图片检测</li>
        <li>检测完成后可查看概率、风险等级与热力图</li>
      </ul>
    </section>
  </aside>
</template>

<script setup>
const steps = [
  { title: '上传图片', desc: '拖拽或选择待检测人脸图片' },
  { title: '特征提取', desc: '人脸裁剪 + 频域 FFT + 空域 CNN' },
  { title: '融合推理', desc: '双分支特征融合，输出伪造概率' },
  { title: '结果可视化', desc: '风险等级 + Grad-CAM 可疑区域' }
]

const techItems = [
  { icon: '🌊', title: '频域分支', desc: 'FFT 幅度谱捕捉高频伪影与压缩残留' },
  { icon: '🎯', title: '空域分支', desc: 'CNN 纹理分析，识别换脸边界痕迹' },
  { icon: '🔥', title: '热力图', desc: 'Grad-CAM 高亮模型关注区域' }
]
</script>

<style scoped>
.guide-panel {
  display: grid;
  gap: 16px;
}

.guide-block {
  background: #fff;
  border: 1px solid #dbe3ec;
  border-radius: 14px;
  padding: 20px;
}

.guide-block h3 {
  margin: 0 0 16px;
  font-size: 15px;
  color: #0f172a;
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
  width: 28px;
  height: 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #166534, #15803d);
  color: #fff;
  font-size: 13px;
  font-weight: 700;
}

.steps strong {
  display: block;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 2px;
}

.steps p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
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
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #eef2f6;
}

.tech-icon {
  font-size: 22px;
  flex-shrink: 0;
}

.tech-card strong {
  display: block;
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 2px;
}

.tech-card p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

.tips ul {
  margin: 0;
  padding-left: 18px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.8;
}
</style>
