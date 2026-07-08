package com.faceshield.mobile.network

import com.faceshield.mobile.auth.AuthTokenStore
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import kotlinx.coroutines.flow.first

class AuthInterceptor(private val tokenStore: AuthTokenStore) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        if (originalRequest.url.encodedPath.contains("api/auth/login")) {
            return chain.proceed(originalRequest)
        }

        val token = runBlocking {
            try {
                tokenStore.accessToken.first()
            } catch (_: Exception) {
                null
            }
        }

        val requestBuilder = originalRequest.newBuilder()
        if (!token.isNullOrEmpty()) {
            requestBuilder.header("Authorization", "Bearer $token")
        }

        return chain.proceed(requestBuilder.build())
    }
}
