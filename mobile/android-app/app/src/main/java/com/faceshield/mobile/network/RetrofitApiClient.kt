package com.faceshield.mobile.network

import android.content.Context
import com.faceshield.mobile.BuildConfig
import com.faceshield.mobile.auth.AuthRepository
import com.faceshield.mobile.auth.AuthTokenStore
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

class RetrofitApiClient(private val context: Context) {

    private val tokenStore = AuthTokenStore(context)
    private var authRepository: AuthRepository? = null

    private var currentBaseUrl: String = ""
    private var retrofit: Retrofit? = null
    private var api: FaceShieldApi? = null

    private val gson: Gson = GsonBuilder()
        .setLenient()
        .create()

    val authTokenStore: AuthTokenStore get() = tokenStore

    fun setAuthRepository(repo: AuthRepository) {
        if (authRepository === repo) return

        authRepository = repo
        if (currentBaseUrl.isNotBlank()) {
            val nextRetrofit = buildRetrofit(currentBaseUrl)
            retrofit = nextRetrofit
            api = nextRetrofit.create(FaceShieldApi::class.java)
        }
    }

    fun getApi(baseUrl: String): FaceShieldApi {
        val normalizedBaseUrl = ServerUrl.normalizeOrThrow(baseUrl)
        if (api == null || normalizedBaseUrl != currentBaseUrl) {
            currentBaseUrl = normalizedBaseUrl
            val nextRetrofit = buildRetrofit(normalizedBaseUrl)
            retrofit = nextRetrofit
            api = nextRetrofit.create(FaceShieldApi::class.java)
        }
        return api ?: error("FaceShieldApi was not initialized.")
    }

    fun updateBaseUrl(baseUrl: String): FaceShieldApi {
        val normalizedBaseUrl = ServerUrl.normalizeOrThrow(baseUrl)
        currentBaseUrl = normalizedBaseUrl
        val nextRetrofit = buildRetrofit(normalizedBaseUrl)
        retrofit = nextRetrofit
        api = nextRetrofit.create(FaceShieldApi::class.java)
        return api ?: error("FaceShieldApi was not initialized.")
    }

    private fun buildRetrofit(baseUrl: String): Retrofit {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
            redactHeader("Authorization")
        }

        val clientBuilder = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .writeTimeout(120, TimeUnit.SECONDS)
            .addInterceptor(AuthInterceptor(tokenStore))
            .addInterceptor(loggingInterceptor)

        authRepository?.let { repo ->
            clientBuilder.addInterceptor(TokenExpiredInterceptor(repo))
        }

        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(clientBuilder.build())
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
}
