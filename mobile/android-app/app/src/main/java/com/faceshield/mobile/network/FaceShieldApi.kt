package com.faceshield.mobile.network

import com.faceshield.mobile.model.ApiResponse
import com.faceshield.mobile.model.DetectionResponse
import com.faceshield.mobile.model.LoginResponse
import com.faceshield.mobile.model.MobileBootstrapResponse
import com.faceshield.mobile.model.ModelVersionResponse
import com.faceshield.mobile.model.RecordsResponse
import com.faceshield.mobile.model.UserProfileDto
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

interface FaceShieldApi {

    @GET("api/mobile/bootstrap")
    suspend fun getMobileBootstrap(): Response<ApiResponse<MobileBootstrapResponse>>

    @POST("api/auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<ApiResponse<LoginResponse>>

    @GET("api/auth/me")
    suspend fun getMe(): Response<ApiResponse<UserProfileDto>>

    @Multipart
    @POST("api/detect")
    suspend fun detect(
        @Part file: MultipartBody.Part
    ): Response<ApiResponse<DetectionResponse>>

    @GET("api/records")
    suspend fun getRecords(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 10
    ): Response<ApiResponse<RecordsResponse>>

    @GET("api/records/{recordId}")
    suspend fun getRecordDetail(
        @Path("recordId") recordId: Int
    ): Response<ApiResponse<DetectionResponse>>

    @GET("api/model-version")
    suspend fun getModelVersion(): Response<ApiResponse<ModelVersionResponse>>
}

data class LoginRequest(
    val username: String,
    val password: String
)
