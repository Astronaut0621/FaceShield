package com.faceshield.mobile.auth

import com.faceshield.mobile.model.LoginResult
import com.faceshield.mobile.network.ServerUrl

class LoginUseCase(private val authRepository: AuthRepository) {

    suspend fun execute(username: String, password: String, serverUrl: String): LoginResult {
        val normalizedServerUrl = ServerUrl.normalizeOrNull(serverUrl)
        if (username.isBlank()) return LoginResult.INVALID_CREDENTIALS
        if (password.isBlank()) return LoginResult.INVALID_CREDENTIALS
        if (normalizedServerUrl == null) return LoginResult.INVALID_SERVER_URL

        return authRepository.login(username, password, normalizedServerUrl)
    }
}
