package com.faceshield.mobile.ui.screen

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.faceshield.mobile.FaceShieldApp
import com.faceshield.mobile.network.ServerUrl
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    val app = context.applicationContext as FaceShieldApp

    var serverUrl by remember { mutableStateOf("") }
    var statusMessage by remember { mutableStateOf<String?>(null) }
    var isStatusError by remember { mutableStateOf(false) }
    var showLogoutDialog by remember { mutableStateOf(false) }
    var logoutSuccess by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        serverUrl = app.authTokenStore.serverUrl.firstOrNull().orEmpty()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("设置") },
                navigationIcon = {
                    TextButton(onClick = onBack) {
                        Text("返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
        ) {
            OutlinedTextField(
                value = serverUrl,
                onValueChange = {
                    serverUrl = it
                    statusMessage = null
                },
                label = { Text("后端地址") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                trailingIcon = {
                    TextButton(onClick = {
                        val normalizedServerUrl = ServerUrl.normalizeOrNull(serverUrl)
                        if (normalizedServerUrl == null) {
                            isStatusError = true
                            statusMessage = "后端地址必须是有效的 http:// 或 https:// 地址"
                            return@TextButton
                        }
                        coroutineScope.launch {
                            runCatching {
                                app.authTokenStore.updateServerUrl(normalizedServerUrl)
                                app.ensureAuthRepository(normalizedServerUrl)
                            }.onSuccess {
                                serverUrl = normalizedServerUrl
                                isStatusError = false
                                statusMessage = "后端地址已保存"
                            }.onFailure {
                                isStatusError = true
                                statusMessage = "后端地址保存失败"
                            }
                        }
                    }) {
                        Text("保存")
                    }
                }
            )

            statusMessage?.let {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = it,
                    color = if (isStatusError) {
                        MaterialTheme.colorScheme.error
                    } else {
                        MaterialTheme.colorScheme.primary
                    },
                    style = MaterialTheme.typography.bodySmall
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("隐私说明", style = MaterialTheme.typography.titleMedium)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "FaceShield 仅在您点击悬浮按钮时截取当前屏幕，截图会上传至您配置的后端进行 AI 换脸检测。您可以随时停止防护。",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            OutlinedButton(
                onClick = { showLogoutDialog = true },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("退出登录", color = MaterialTheme.colorScheme.error)
            }
        }
    }

    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = { Text("退出登录") },
            text = { Text("确定要退出登录吗？") },
            confirmButton = {
                TextButton(onClick = {
                    showLogoutDialog = false
                    coroutineScope.launch {
                        runCatching { app.authRepository.logout() }
                            .onSuccess { logoutSuccess = true }
                            .onFailure {
                                isStatusError = true
                                statusMessage = "退出登录失败，请重试"
                            }
                    }
                }) {
                    Text("确定", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text("取消")
                }
            }
        )
    }

    if (logoutSuccess) {
        LaunchedEffect(Unit) { onBack() }
    }
}
