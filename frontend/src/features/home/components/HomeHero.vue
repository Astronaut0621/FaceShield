<template>
  <section class="hero-content">
    <p class="hero-kicker">AI 换脸诈骗 · 伪造人脸检测平台</p>
    <h1 class="hero-title">FaceShield</h1>
    <p class="hero-desc">
      融合频域与空域深度特征，精准识别 DeepFake 换脸伪造痕迹，<br />
      输出伪造概率、风险等级与可疑区域热力图，守护数字身份安全。
    </p>
    <RouterLink class="hero-cta" to="/login?redirect=/detective">
      开始检测
    </RouterLink>
  </section>
</template>

<style scoped>
.hero-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 24px 120px;
  color: #fff;
}

.hero-kicker {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.04em;
  opacity: 0.92;
}

.hero-title {
  margin: 0;
  font-size: clamp(64px, 12vw, 120px);
  font-weight: 800;
  letter-spacing: 0.06em;
  line-height: 1;
  text-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
}

.hero-desc {
  margin: 24px 0 36px;
  max-width: 560px;
  font-size: 15px;
  line-height: 1.8;
  opacity: 0.9;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  padding: 0 32px;
  border-radius: 10px;
  background: #166534;
  color: #fff;
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  box-shadow: 0 8px 24px rgba(22, 101, 52, 0.35);
  transition: background 0.15s, transform 0.15s;
}

.hero-cta:hover {
  background: #15803d;
  transform: translateY(-1px);
}
</style>
