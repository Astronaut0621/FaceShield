package com.faceshield.mobile

import android.app.Application
import com.faceshield.mobile.auth.AuthRepository
import com.faceshield.mobile.auth.AuthTokenStore
import com.faceshield.mobile.auth.CurrentUserSession
import com.faceshield.mobile.network.FaceShieldApi
import com.faceshield.mobile.network.RetrofitApiClient
import com.faceshield.mobile.network.ServerUrl

class FaceShieldApp : Application() {
    val apiClient: RetrofitApiClient by lazy { RetrofitApiClient(this) }
    val authTokenStore: AuthTokenStore by lazy { apiClient.authTokenStore }

    private var _authRepository: AuthRepository? = null
    private var _currentUserSession: CurrentUserSession? = null
    private var _currentServerUrl: String = ""

    val authRepository: AuthRepository
        get() = _authRepository ?: throw IllegalStateException("AuthRepository not initialized. Call ensureAuthRepository first.")

    val currentUserSession: CurrentUserSession
        get() = _currentUserSession ?: throw IllegalStateException("CurrentUserSession not initialized. Call ensureAuthRepository first.")

    fun ensureAuthRepository(serverUrl: String): AuthRepository {
        val normalizedServerUrl = ServerUrl.normalizeOrThrow(serverUrl)
        if (_authRepository == null || normalizedServerUrl != _currentServerUrl) {
            _currentServerUrl = normalizedServerUrl
            val api = apiClient.getApi(normalizedServerUrl)
            val repository = AuthRepository(api, authTokenStore)
            _authRepository = repository
            _currentUserSession = CurrentUserSession(repository)
            apiClient.setAuthRepository(repository)
        }
        return _authRepository ?: error("AuthRepository was not initialized.")
    }

    fun getApi(serverUrl: String): FaceShieldApi {
        return apiClient.getApi(ServerUrl.normalizeOrThrow(serverUrl))
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
    }

    companion object {
        lateinit var instance: FaceShieldApp
            private set
    }
}
