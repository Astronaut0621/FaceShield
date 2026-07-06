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
      <div class="features-grid">
        <article v-for="item in features" :key="item.title" class="feature-card">
          <span class="feature-icon">{{ item.icon }}</span>
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
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #e8ecef;
}

.hero-shell {
  padding: 20px;
  min-height: 100vh;
  box-sizing: border-box;
}

.hero-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 40px);
  border-radius: 24px;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(6, 18, 40, 0.8) 0%, rgba(6, 18, 40, 0.83) 100%),
    url('/images/home-hero-bg.png') center / cover no-repeat;
}

.hero-footer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 32px;
  z-index: 2;
}

.features-section {
  max-width: 960px;
  margin: 0 auto;
  padding: 48px 24px 64px;
}

.features-section h2 {
  margin: 0 0 28px;
  text-align: center;
  font-size: 24px;
  color: #0f172a;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.feature-card {
  background: #fff;
  border-radius: 14px;
  padding: 24px 20px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.feature-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #0f172a;
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
}
</style>
