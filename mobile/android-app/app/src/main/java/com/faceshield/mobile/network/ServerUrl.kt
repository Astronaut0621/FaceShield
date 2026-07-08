package com.faceshield.mobile.network

import java.net.URI

object ServerUrl {
    const val DEFAULT = "http://10.0.2.2:8000/"

    fun normalizeOrNull(rawUrl: String): String? {
        val trimmed = rawUrl.trim()
        if (trimmed.isBlank()) return null

        val uri = runCatching { URI(trimmed) }.getOrNull() ?: return null
        val scheme = uri.scheme?.lowercase() ?: return null
        if (scheme != "http" && scheme != "https") return null
        if (uri.host.isNullOrBlank()) return null
        if (uri.userInfo != null) return null
        if (uri.rawQuery != null || uri.rawFragment != null) return null

        return if (trimmed.endsWith("/")) trimmed else "$trimmed/"
    }

    fun normalizeOrThrow(rawUrl: String): String {
        return normalizeOrNull(rawUrl)
            ?: throw IllegalArgumentException("Backend URL must be a valid http:// or https:// URL.")
    }

    fun normalizeOrDefault(rawUrl: String?): String {
        return normalizeOrNull(rawUrl.orEmpty()) ?: DEFAULT
    }
}
