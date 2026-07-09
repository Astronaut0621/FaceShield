package com.faceshield.mobile.ui.screen

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.faceshield.mobile.FaceShieldApp
import com.faceshield.mobile.auth.LoginUseCase
import com.faceshield.mobile.model.LoginResult
import com.faceshield.mobile.network.ServerUrl
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch

@Composable
fun LoginScreen(onLoginSuccess: () -> Unit) {
    var username by remember { mutableStateOf("demo") }
    var password by remember { mutableStateOf("demo123456") }
    var serverUrl by remember { mutableStateOf(ServerUrl.DEFAULT) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }

    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    LaunchedEffect(Unit) {
        val app = context.applicationContext as FaceShieldApp
        serverUrl = app.authTokenStore.serverUrl.firstOrNull().orEmpty().ifBlank {
            ServerUrl.DEFAULT
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "FaceShield",
            style = MaterialTheme.typography.headlineLarge,
            color = MaterialTheme.colorScheme.primary
        )

        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = "移动端 AI 换脸检测",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(40.dp))

        OutlinedTextField(
            value = serverUrl,
            onValueChange = { serverUrl = it; errorMessage = null },
            label = { Text("后端地址") },
            placeholder = { Text("http://10.0.2.2:8000/") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            enabled = !isLoading
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = username,
            onValueChange = { username = it; errorMessage = null },
            label = { Text("用户名") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            enabled = !isLoading
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it; errorMessage = null },
            label = { Text("密码") },
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            enabled = !isLoading
        )

        errorMessage?.let {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = it,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall
            )
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = {
                isLoading = true
                errorMessage = null
                val normalizedServerUrl = ServerUrl.normalizeOrNull(serverUrl)
                if (normalizedServerUrl == null) {
                    isLoading = false
                    errorMessage = "后端地址必须是有效的 http:// 或 https:// 地址"
                    return@Button
                }
                val app = context.applicationContext as FaceShieldApp
                val loginUseCase = LoginUseCase(app.ensureAuthRepository(normalizedServerUrl))

                coroutineScope.launch {
                    val result = loginUseCase.execute(username, password, normalizedServerUrl)
                    isLoading = false
                    when (result) {
                        LoginResult.SUCCESS -> onLoginSuccess()
                        LoginResult.INVALID_CREDENTIALS -> errorMessage = "用户名或密码无效"
                        LoginResult.NETWORK_ERROR -> errorMessage = "网络错误，请检查网络连接"
                        LoginResult.SERVER_UNREACHABLE -> errorMessage = "无法连接到后端服务器"
                        LoginResult.BACKEND_UNHEALTHY -> errorMessage = "后端服务未就绪，暂不支持移动端登录"
                        LoginResult.INVALID_SERVER_URL -> errorMessage = "后端地址必须是有效的 http:// 或 https:// 地址"
                    }
                }
            },
            modifier = Modifier.fillMaxWidth(),
            enabled = !isLoading && username.isNotBlank() && password.isNotBlank() && serverUrl.isNotBlank()
        ) {
            if (isLoading) {
                Text("登录中...")
            } else {
                Text("登录")
            }
        }
    }
}
