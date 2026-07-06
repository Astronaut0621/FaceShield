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
  { code: 'FFT', title: '频域分支', desc: '幅度谱捕捉高频伪影与压缩残留' },
  { code: 'CNN', title: '空域分支', desc: '纹理分析识别换脸边界痕迹' },
  { code: 'CAM', title: '热力图', desc: 'Grad-CAM 高亮模型关注区域' }
]
</script>

<style scoped>
.guide-panel {
  display: grid;
  gap: 14px;
}

.guide-block {
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid #d8e4de;
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 14px 34px rgba(16, 35, 27, 0.05);
}

.guide-block h3 {
  margin: 0 0 16px;
  font-size: 15px;
  color: #10231b;
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
  background: #e1f4eb;
  color: #065f36;
  font-size: 13px;
  font-weight: 900;
}

.steps strong {
  display: block;
  font-size: 14px;
  color: #10231b;
  margin-bottom: 2px;
}

.steps p {
  margin: 0;
  font-size: 13px;
  color: #60756b;
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
  background: #f6faf8;
  border: 1px solid #e5eee9;
}

.tech-icon {
  width: 42px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: #10231b;
  color: #5eeaa2;
  font-size: 11px;
  font-weight: 900;
  flex-shrink: 0;
}

.tech-card strong {
  display: block;
  font-size: 13px;
  color: #10231b;
  margin-bottom: 2px;
}

.tech-card p {
  margin: 0;
  font-size: 12px;
  color: #60756b;
  line-height: 1.5;
}

.tips ul {
  margin: 0;
  padding-left: 18px;
  color: #60756b;
  font-size: 13px;
  line-height: 1.85;
}
</style>
