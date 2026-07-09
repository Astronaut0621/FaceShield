package com.faceshield.mobile.detection

import com.faceshield.mobile.model.DetectionResult
import com.faceshield.mobile.model.NetworkResult
import com.faceshield.mobile.model.RecordsResponse
import com.faceshield.mobile.model.RiskLevel
import com.faceshield.mobile.network.FaceShieldApi
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.net.SocketTimeoutException
import java.net.UnknownHostException

class DetectionRepository(private val api: FaceShieldApi) {

    suspend fun detect(file: File): NetworkResult<DetectionResult> {
        return try {
            val requestBody = file.asRequestBody("image/jpeg".toMediaTypeOrNull())
            val part = MultipartBody.Part.createFormData("file", file.name, requestBody)

            val response = api.detect(part)
            if (response.isSuccessful) {
                val data = response.body()?.data
                if (data != null) {
                    NetworkResult.Success(
                        DetectionResult(
                            taskId = data.taskId,
                            fileId = data.fileId,
                            label = data.label ?: data.prediction ?: "未知",
                            fakeProbability = data.fakeProbability,
                            confidence = data.confidence,
                            riskLevel = RiskLevel.fromString(data.riskLevel),
                            faceDetected = data.faceDetected ?: false,
                            faceCropUrl = data.faceCropUrl,
                            heatmapUrl = data.heatmapUrl,
                            frequencyScore = data.frequencyScore,
                            spatialScore = data.spatialScore,
                            suggestion = data.suggestion,
                            modelName = data.modelName,
                            modelVersion = data.modelVersion,
                            originalImageUrl = data.originalImageUrl,
                            originalFilename = data.originalFilename,
                            createdAt = data.createdAt
                        )
                    )
                } else {
                    NetworkResult.Error(response.code(), "检测响应数据为空")
                }
            } else if (response.code() == 401) {
                NetworkResult.Error(401, "登录已过期")
            } else {
                NetworkResult.Error(response.code(), "检测失败：${response.message()}")
            }
        } catch (e: SocketTimeoutException) {
            NetworkResult.Error(0, "请求超时")
        } catch (e: UnknownHostException) {
            NetworkResult.Error(0, "无法连接到服务器")
        } catch (e: Exception) {
            NetworkResult.Exception(e)
        }
    }

    suspend fun getRecords(page: Int, pageSize: Int): NetworkResult<RecordsResponse> {
        return try {
            val response = api.getRecords(page, pageSize)
            if (response.isSuccessful) {
                response.body()?.data?.let { NetworkResult.Success(it) }
                    ?: NetworkResult.Error(response.code(), "记录响应数据为空")
            } else {
                NetworkResult.Error(response.code(), "查询记录失败")
            }
        } catch (e: Exception) {
            NetworkResult.Exception(e)
        }
    }

    suspend fun getRecordDetail(recordId: Int): NetworkResult<DetectionResult> {
        return try {
            val response = api.getRecordDetail(recordId)
            if (response.isSuccessful) {
                val data = response.body()?.data
                if (data != null) {
                    NetworkResult.Success(
                        DetectionResult(
                            taskId = data.taskId,
                            fileId = data.fileId,
                            label = data.label ?: data.prediction ?: "未知",
                            fakeProbability = data.fakeProbability,
                            confidence = data.confidence,
                            riskLevel = RiskLevel.fromString(data.riskLevel),
                            faceDetected = data.faceDetected ?: false,
                            faceCropUrl = data.faceCropUrl,
                            heatmapUrl = data.heatmapUrl,
                            frequencyScore = data.frequencyScore,
                            spatialScore = data.spatialScore,
                            suggestion = data.suggestion,
                            modelName = data.modelName,
                            modelVersion = data.modelVersion,
                            originalImageUrl = data.originalImageUrl,
                            originalFilename = data.originalFilename,
                            createdAt = data.createdAt
                        )
                    )
                } else {
                    NetworkResult.Error(response.code(), "记录详情为空")
                }
            } else {
                NetworkResult.Error(response.code(), "查询记录详情失败")
            }
        } catch (e: Exception) {
            NetworkResult.Exception(e)
        }
    }
}
