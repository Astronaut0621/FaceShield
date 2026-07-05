const RISK_LABELS = {
  low: '低风险',
  medium: '中风险',
  high: '高风险'
}

const LABEL_TEXT = {
  real: '真实人脸',
  fake: '伪造人脸'
}

export function formatPercent(value, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-'
  const num = Number(value)
  const percent = num <= 1 ? num * 100 : num
  return `${percent.toFixed(digits)}%`
}

export function formatRiskLevel(level) {
  if (!level) return '-'
  return RISK_LABELS[level] || level
}

export function formatLabel(label) {
  if (!label) return '-'
  return LABEL_TEXT[label] || label
}

export function formatDateTime(value) {
  if (!value) return '-'
  const date = new Date(value.replace(' ', 'T'))
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function riskLevelClass(level) {
  return level ? `risk-${level}` : ''
}
