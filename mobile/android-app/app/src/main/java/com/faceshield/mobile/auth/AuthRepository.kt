package com.faceshield.mobile.auth

import com.faceshield.mobile.model.LoginResult
import com.faceshield.mobile.model.UserProfileDto
import com.faceshield.mobile.network.FaceShieldApi
import com.faceshield.mobile.network.LoginRequest
import com.faceshield.mobile.network.ServerUrl
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.firstOrNull
import java.net.SocketTimeoutException
import java.net.UnknownHostException

class AuthRepository(
    private val api: FaceShieldApi,
    private val tokenStore: AuthTokenStore
) {
    private val _userProfile = MutableStateFlow<UserProfileDto?>(null)
    val userProfile: StateFlow<UserProfileDto?> = _userProfile.asStateFlow()

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()

    suspend fun login(username: String, password: String, serverUrl: String): LoginResult {
        if (username.isBlank() || password.isBlank()) {
            return LoginResult.INVALID_CREDENTIALS
        }
        val normalizedServerUrl = ServerUrl.normalizeOrNull(serverUrl)
        if (normalizedServerUrl == null) {
            return LoginResult.INVALID_SERVER_URL
        }

        return try {
            val bootstrapResponse = api.getMobileBootstrap()
            if (!bootstrapResponse.isSuccessful) {
                return LoginResult.SERVER_UNREACHABLE
            }
            val bootstrap = bootstrapResponse.body()?.data
            if (bootstrap?.status != "ok") {
                return LoginResult.BACKEND_UNHEALTHY
            }

            val response = api.login(LoginRequest(username, password))
            if (response.isSuccessful) {
                val body = response.body()
                val data = body?.data
                if (data != null) {
                    tokenStore.saveToken(data.accessToken, normalizedServerUrl, data.user.username)
                    _userProfile.value = data.user
                    _isLoggedIn.value = true
                    LoginResult.SUCCESS
                } else {
                    LoginResult.INVALID_CREDENTIALS
                }
            } else {
                if (response.code() == 401 || response.code() == 400) {
                    LoginResult.INVALID_CREDENTIALS
                } else {
                    LoginResult.SERVER_UNREACHABLE
                }
            }
        } catch (e: SocketTimeoutException) {
            LoginResult.SERVER_UNREACHABLE
        } catch (e: UnknownHostException) {
            LoginResult.SERVER_UNREACHABLE
        } catch (e: Exception) {
            LoginResult.NETWORK_ERROR
        }
    }

    suspend fun logout() {
        tokenStore.clearToken()
        _userProfile.value = null
        _isLoggedIn.value = false
    }

    suspend fun handleTokenExpired() {
        tokenStore.clearToken()
        _userProfile.value = null
        _isLoggedIn.value = false
    }

    suspend fun refreshFromStore() {
        val hasToken = tokenStore.hasTokenSync()
        _isLoggedIn.value = hasToken
        if (hasToken) {
            val name = tokenStore.username.firstOrNull()
            if (name != null) {
                _userProfile.value = UserProfileDto(
                    id = 0,
                    username = name,
                    displayName = null,
                    status = "active",
                    lastLoginAt = null
                )
            }
        }
    }

}
