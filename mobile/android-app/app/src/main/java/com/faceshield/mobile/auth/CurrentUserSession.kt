package com.faceshield.mobile.auth

import com.faceshield.mobile.model.UserProfileDto
import kotlinx.coroutines.flow.StateFlow

class CurrentUserSession(private val authRepository: AuthRepository) {

    val userProfile: StateFlow<UserProfileDto?> = authRepository.userProfile
    val isLoggedIn: StateFlow<Boolean> = authRepository.isLoggedIn

    suspend fun refresh() {
        authRepository.refreshFromStore()
    }

    suspend fun clear() {
        authRepository.handleTokenExpired()
    }
}