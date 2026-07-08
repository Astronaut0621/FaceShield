package com.faceshield.mobile.model

data class DetectionResult(
    val taskId: Int,
    val fileId: Int,
    val label: String,
    val fakeProbability: Double?,
    val confidence: Double?,
    val riskLevel: RiskLevel,
    val faceDetected: Boolean,
    val faceCropUrl: String?,
    val heatmapUrl: String?,
    val frequencyScore: Double?,
    val spatialScore: Double?,
    val suggestion: String?,
    val modelName: String?,
    val modelVersion: String?,
    val originalImageUrl: String?,
    val originalFilename: String?,
    val createdAt: String?
)
