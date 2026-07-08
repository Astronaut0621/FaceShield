package com.faceshield.mobile.model

enum class LoginResult {
    SUCCESS,
    INVALID_CREDENTIALS,
    NETWORK_ERROR,
    SERVER_UNREACHABLE,
    BACKEND_UNHEALTHY,
    INVALID_SERVER_URL
}
