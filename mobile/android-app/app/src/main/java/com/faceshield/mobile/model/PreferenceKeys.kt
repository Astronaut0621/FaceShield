package com.faceshield.mobile.model

import androidx.datastore.preferences.core.stringPreferencesKey

object PreferenceKeys {
    val ACCESS_TOKEN = stringPreferencesKey("access_token")
    val SERVER_URL = stringPreferencesKey("server_url")
    val USERNAME = stringPreferencesKey("username")
    val LAST_LOGIN_AT = stringPreferencesKey("last_login_at")
}

data class AppConfig(
    val serverUrl: String = "",
    val username: String = "",
    val isLoggedIn: Boolean = false
)