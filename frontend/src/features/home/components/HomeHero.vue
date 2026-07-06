<template>
  <section class="hero-content">
    <div class="hero-copy">
      <p class="hero-kicker">AI 换脸伪造检测平台</p>
      <h1 class="hero-title">FaceShield</h1>
      <p class="hero-desc">
        融合频域与空域特征，识别 DeepFake 痕迹，并输出风险等级与热力图。
      </p>
      <div class="hero-actions">
        <RouterLink class="hero-cta" to="/login?redirect=/detective">开始检测</RouterLink>
        <RouterLink class="hero-link" to="/history">查看历史</RouterLink>
      </div>
    </div>

    <div class="hero-visual" aria-label="检测流程预览">
      <div class="scan-card main-card">
        <span class="scan-label">检测结论</span>
        <strong>疑似伪造</strong>
        <p>模型关注区域集中在人脸边界与眼周纹理。</p>
      </div>
      <div class="face-frame">
        <img src="/images/home-hero-bg.png" alt="人脸检测示例" />
        <span class="focus-box focus-one" />
        <span class="focus-box focus-two" />
      </div>
      <div class="scan-card metric-card">
        <span class="scan-label">伪造概率</span>
        <strong>87.4%</strong>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-content {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(340px, 1.05fr);
  align-items: center;
  gap: clamp(28px, 6vw, 74px);
  padding: clamp(40px, 7vw, 82px) clamp(22px, 6vw, 74px) 150px;
  color: var(--text);
}

.hero-copy {
  max-width: 560px;
}

.hero-kicker {
  width: fit-content;
  margin: 0 0 16px;
  padding: 7px 11px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 13px;
  font-weight: 750;
}

.hero-title {
  margin: 0;
  font-size: clamp(56px, 9vw, 108px);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 0.95;
}

.hero-desc {
  margin: 22px 0 30px;
  max-width: 520px;
  color: var(--muted);
  font-size: clamp(16px, 2vw, 19px);
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-cta,
.hero-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 24px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 15px;
  font-weight: 750;
  transition:
    transform 0.16s ease,
    background 0.16s ease,
    box-shadow 0.16s ease;
}

.hero-cta {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.24);
}

.hero-link {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--line);
}

.hero-cta:hover {
  background: var(--accent-strong);
  transform: translateY(-1px);
}

.hero-link:hover {
  background: var(--surface-soft);
  transform: translateY(-1px);
}

.hero-visual {
  position: relative;
  min-height: 440px;
}

.face-frame {
  position: absolute;
  inset: 28px 0 0 52px;
  overflow: hidden;
  border-radius: 24px;
  border: 1px solid rgba(23, 32, 51, 0.14);
  background: var(--text);
  box-shadow: 0 28px 70px rgba(23, 32, 51, 0.2);
}

.face-frame img {
  width: 100%;
  height: 100%;
  min-height: 390px;
  object-fit: cover;
  opacity: 0.88;
  filter: saturate(0.9) contrast(1.02);
}

.face-frame::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, transparent 0%, rgba(23, 32, 51, 0.52) 100%),
    repeating-linear-gradient(
      0deg,
      rgba(255, 255, 255, 0.08) 0,
      rgba(255, 255, 255, 0.08) 1px,
      transparent 1px,
      transparent 22px
    );
}

.focus-box {
  position: absolute;
  z-index: 2;
  border: 2px solid var(--accent-glow);
  border-radius: 16px;
  box-shadow: 0 0 0 5px rgba(147, 197, 253, 0.16);
}

.focus-one {
  width: 34%;
  height: 22%;
  left: 32%;
  top: 26%;
}

.focus-two {
  width: 42%;
  height: 28%;
  left: 28%;
  top: 53%;
}

.scan-card {
  position: absolute;
  z-index: 3;
  display: grid;
  gap: 7px;
  padding: 17px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(216, 224, 236, 0.9);
  box-shadow: 0 18px 46px rgba(23, 32, 51, 0.14);
}

.main-card {
  left: 0;
  top: 0;
  width: min(260px, 60%);
}

.metric-card {
  right: 22px;
  bottom: 18px;
  min-width: 160px;
}

.scan-label {
  color: var(--muted);
  font-size: 12px;
  font-weight: 750;
}

.scan-card strong {
  color: var(--text);
  font-size: 26px;
  line-height: 1;
}

.scan-card p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.55;
}

@media (max-width: 900px) {
  .hero-content {
    grid-template-columns: 1fr;
    padding: 34px 18px 24px;
  }

  .hero-visual {
    min-height: 360px;
  }

  .face-frame {
    inset: 36px 0 0 22px;
  }
}

@media (max-width: 560px) {
  .hero-title {
    font-size: 54px;
  }

  .hero-actions {
    display: grid;
  }

  .hero-cta,
  .hero-link {
    width: 100%;
  }

  .main-card {
    width: calc(100% - 36px);
  }

  .metric-card {
    right: 10px;
    bottom: 8px;
  }
}
</style>
