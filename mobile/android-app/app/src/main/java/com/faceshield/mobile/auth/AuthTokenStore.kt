package com.faceshield.mobile.auth

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import com.faceshield.mobile.model.PreferenceKeys
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.map

private val Context.authDataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")

class AuthTokenStore(private val context: Context) {

    val accessToken: Flow<String?> = context.authDataStore.data.map { prefs ->
        prefs[PreferenceKeys.ACCESS_TOKEN]
    }

    val serverUrl: Flow<String?> = context.authDataStore.data.map { prefs ->
        prefs[PreferenceKeys.SERVER_URL]
    }

    val username: Flow<String?> = context.authDataStore.data.map { prefs ->
        prefs[PreferenceKeys.USERNAME]
    }

    val hasToken: Flow<Boolean> = accessToken.map { it != null && it.isNotEmpty() }

    suspend fun hasTokenSync(): Boolean {
        return !accessToken.firstOrNull().isNullOrBlank()
    }

    suspend fun saveToken(token: String, serverUrl: String, username: String) {
        context.authDataStore.edit { prefs ->
            prefs[PreferenceKeys.ACCESS_TOKEN] = token
            prefs[PreferenceKeys.SERVER_URL] = serverUrl
            prefs[PreferenceKeys.USERNAME] = username
            prefs[PreferenceKeys.LAST_LOGIN_AT] = System.currentTimeMillis().toString()
        }
    }

    suspend fun clearToken() {
        context.authDataStore.edit { prefs ->
            prefs.remove(PreferenceKeys.ACCESS_TOKEN)
            prefs.remove(PreferenceKeys.USERNAME)
            prefs.remove(PreferenceKeys.LAST_LOGIN_AT)
        }
    }

    suspend fun updateServerUrl(url: String) {
        context.authDataStore.edit { prefs ->
            prefs[PreferenceKeys.SERVER_URL] = url
        }
    }
}
