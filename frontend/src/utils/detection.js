export function normalizeDetectionResult(raw) {
  if (!raw) return null

  const originalImageUrl =
    raw.original_image_url || raw.file_url || raw.file?.file_url || null

  return {
    taskId: raw.task_id ?? raw.record_id ?? null,
    fileId: raw.file_id ?? raw.file?.file_id ?? null,
    label: raw.label ?? raw.prediction ?? null,
    fakeProbability: raw.fake_probability ?? null,
    confidence: raw.confidence ?? null,
    riskLevel: raw.risk_level ?? null,
    frequencyScore: raw.frequency_score ?? null,
    spatialScore: raw.spatial_score ?? null,
    heatmapUrl: raw.heatmap_url ?? null,
    faceCropUrl: raw.face_crop_url ?? null,
    faceDetected: raw.face_detected ?? null,
    suggestion: raw.suggestion ?? null,
    modelName: raw.model_name ?? null,
    modelVersion: raw.model_version ?? null,
    createdAt: raw.created_at ?? null,
    originalFilename: raw.original_filename ?? raw.file?.original_filename ?? null,
    originalImageUrl
  }
}
