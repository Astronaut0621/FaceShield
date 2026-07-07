package com.faceshield.mobile.model

import com.google.gson.annotations.SerializedName

data class LoginResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("expires_in")
    val expiresIn: Int? = null,
    val user: UserProfileDto
)

data class UserProfileDto(
    val id: Int,
    val username: String,
    @SerializedName("display_name")
    val displayName: String?,
    val status: String,
    @SerializedName("last_login_at")
    val lastLoginAt: String?
)

data class DetectionResponse(
    @SerializedName("task_id")
    val taskId: Int,
    @SerializedName("file_id")
    val fileId: Int,
    val label: String?,
    val prediction: String?,
    @SerializedName("fake_probability")
    val fakeProbability: Double?,
    val confidence: Double?,
    @SerializedName("risk_level")
    val riskLevel: String?,
    @SerializedName("original_image_url")
    val originalImageUrl: String?,
    @SerializedName("original_filename")
    val originalFilename: String?,
    @SerializedName("face_crop_url")
    val faceCropUrl: String?,
    @SerializedName("face_detected")
    val faceDetected: Boolean?,
    @SerializedName("heatmap_url")
    val heatmapUrl: String?,
    @SerializedName("frequency_score")
    val frequencyScore: Double?,
    @SerializedName("spatial_score")
    val spatialScore: Double?,
    val suggestion: String?,
    @SerializedName("model_name")
    val modelName: String?,
    @SerializedName("model_version")
    val modelVersion: String?,
    @SerializedName("created_at")
    val createdAt: String?
)

data class RecordsResponse(
    val total: Int = 0,
    val items: List<DetectionResponse> = emptyList()
)

data class ModelVersionResponse(
    @SerializedName("model_name")
    val name: String?,
    val version: String?,
    @SerializedName("is_active")
    val isActive: Boolean?
)
