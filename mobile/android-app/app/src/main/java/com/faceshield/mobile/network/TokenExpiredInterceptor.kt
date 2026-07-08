package com.faceshield.mobile.network

import com.faceshield.mobile.auth.AuthRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.Interceptor
import okhttp3.Response

class TokenExpiredInterceptor(private val authRepository: AuthRepository) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())

        if (response.code == 401) {
            CoroutineScope(Dispatchers.IO).launch {
                authRepository.handleTokenExpired()
            }
        }

        return response
    }
}