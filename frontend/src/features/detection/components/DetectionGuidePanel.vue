<template>
</template>
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
