<template>
  <div class="home-page">
    <div class="hero-shell">
      <div class="hero-card">
        <HomeNav />
        <HomeHero />
        <div class="hero-footer">
          <HomeDetectBar />
        </div>
      </div>
    </div>

    <section id="features" class="features-section">
      <div class="section-heading">
        <h2>从上传到判定，一次完成</h2>
        <p>面向图片取证、身份核验和内容审核场景，保留可解释的检测链路。</p>
      </div>
      <div class="features-grid">
        <article v-for="item in features" :key="item.title" class="feature-card">
          <span class="feature-icon">{{ item.index }}</span>
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import HomeDetectBar from '@/features/home/components/HomeDetectBar.vue'
import HomeHero from '@/features/home/components/HomeHero.vue'
import HomeNav from '@/features/home/components/HomeNav.vue'

const features = [
  {
    index: '01',
    title: '频域特征分析',
    desc: '基于 FFT 幅度谱捕捉 DeepFake 高频伪影与压缩残留。'
  },
  {
    index: '02',
    title: '空域纹理检测',
    desc: 'CNN 提取人脸局部纹理，识别换脸边界与融合痕迹。'
  },
  {
    index: '03',
    title: 'Grad-CAM 热力图',
    desc: '可视化模型关注区域，定位最可疑的伪造部位。'
  },
  {
    index: '04',
    title: '风险等级评估',
    desc: '综合伪造概率输出低、中、高风险，辅助快速决策。'
  }
]
</script>

<style scoped>
.home-page {
  min-height: 100dvh;
  background: #eef3f1;
}

.hero-shell {
  padding: 18px;
  min-height: 100dvh;
}

.hero-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: calc(100dvh - 36px);
  border-radius: 26px;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(246, 250, 248, 0.9)),
    #fff;
  border: 1px solid rgba(216, 228, 222, 0.9);
  box-shadow: 0 28px 80px rgba(16, 35, 27, 0.12);
}

.hero-footer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 28px;
  z-index: 4;
}

.features-section {
  max-width: 1120px;
  margin: 0 auto;
  padding: 54px 24px 72px;
}

.section-heading {
  display: grid;
  gap: 10px;
  margin-bottom: 24px;
}

.section-heading h2 {
  margin: 0;
  color: #10231b;
  font-size: clamp(26px, 4vw, 42px);
  font-weight: 850;
  letter-spacing: -0.02em;
}

.section-heading p {
  margin: 0;
  color: #60756b;
  font-size: 15px;
  max-width: 58ch;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.feature-card {
  display: grid;
  align-content: start;
  min-height: 190px;
  background: #fff;
  border-radius: 18px;
  padding: 22px;
  border: 1px solid #d8e4de;
  box-shadow: 0 14px 36px rgba(16, 35, 27, 0.06);
}

.feature-card:nth-child(2),
.feature-card:nth-child(4) {
  background: #f6faf8;
}

.feature-icon {
  width: 42px;
  height: 34px;
  display: grid;
  place-items: center;
  margin-bottom: 22px;
  border-radius: 11px;
  background: #e1f4eb;
  color: #065f36;
  font-size: 13px;
  font-weight: 850;
}

.feature-card h3 {
  margin: 0 0 9px;
  font-size: 17px;
  color: #10231b;
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  color: #60756b;
  line-height: 1.65;
}

@media (max-width: 980px) {
  .hero-footer {
    position: static;
    padding-bottom: 18px;
  }

  .features-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 580px) {
  .hero-shell {
    padding: 10px;
  }

  .hero-card {
    min-height: auto;
    border-radius: 20px;
  }

  .features-section {
    padding: 40px 16px 52px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
