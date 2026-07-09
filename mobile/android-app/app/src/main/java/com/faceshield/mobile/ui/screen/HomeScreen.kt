package com.faceshield.mobile.ui.screen

import android.content.Intent
import android.net.Uri
import android.provider.Settings
import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Snackbar
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.List
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.ui.draw.clip
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import com.faceshield.mobile.model.ServiceState
import com.faceshield.mobile.service.FaceShieldOverlayService

@Composable
fun HomeScreen(
    onNavigateToSettings: () -> Unit,
    onNavigateToRecords: () -> Unit,
    onNavigateToResult: (taskId: Int) -> Unit,
    onRequestMediaProjection: () -> Unit = {}
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val serviceState by FaceShieldOverlayService.serviceState.collectAsState()
    val startError by FaceShieldOverlayService.startError.collectAsState()
    val isProtectionOn = serviceState != ServiceState.STOPPED
    var pendingOverlayStart by remember { mutableStateOf(false) }
    var localMessage by remember { mutableStateOf<String?>(null) }
    val snackbarHostState = remember { SnackbarHostState() }

    // 启动失败时显示 Snackbar 详细原因
    LaunchedEffect(startError) {
        startError?.let { snackbarHostState.showSnackbar(it) }
    }

    // 服务启动成功后清除临时消息
    LaunchedEffect(serviceState) {
        if (serviceState == ServiceState.RUNNING) {
            localMessage = null
        }
    }

    // 从系统设置页返回后，若已授权悬浮窗权限则自动启动
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME && pendingOverlayStart) {
                if (Settings.canDrawOverlays(context)) {
                    context.startForegroundService(
                        Intent(context, FaceShieldOverlayService::class.java)
                    )
                }
                pendingOverlayStart = false
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    Scaffold(
        snackbarHost = {
            SnackbarHost(hostState = snackbarHostState)
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = true,
                    onClick = {},
                    icon = { Icon(Icons.Outlined.Home, contentDescription = "首页") },
                    label = { Text("首页") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateToRecords,
                    icon = { Icon(Icons.Outlined.List, contentDescription = "记录") },
                    label = { Text("记录") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateToSettings,
                    icon = { Icon(Icons.Outlined.Settings, contentDescription = "设置") },
                    label = { Text("设置") }
                )
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.weight(1f))

            Box(
                modifier = Modifier
                    .size(140.dp)
                    .clip(CircleShape)
                    .background(
                        if (isProtectionOn) MaterialTheme.colorScheme.error
                        else MaterialTheme.colorScheme.primary
                    ),
                contentAlignment = Alignment.Center
            ) {
                IconButton(
                    onClick = {
                        Log.d("HomeScreen", "按钮被点击，isProtectionOn=$isProtectionOn")
                        if (isProtectionOn) {
                            context.startService(
                                Intent(context, FaceShieldOverlayService::class.java).apply {
                                    action = FaceShieldOverlayService.ACTION_STOP
                                }
                            )
                        } else {
                            localMessage = "正在启动..."
                            try {
                                context.startForegroundService(
                                    Intent(context, FaceShieldOverlayService::class.java)
                                )
                            } catch (e: Exception) {
                                localMessage = "启动失败: ${e.localizedMessage}"
                            }
                            if (!Settings.canDrawOverlays(context)) {
                                pendingOverlayStart = true
                                context.startActivity(
                                    Intent(
                                        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                        Uri.parse("package:${context.packageName}")
                                    ).apply {
                                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                                    }
                                )
                            }
                        }
                    },
                    modifier = Modifier.fillMaxSize()
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = if (isProtectionOn) "⏹" else "▶",
                            style = MaterialTheme.typography.displaySmall,
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                        Text(
                            text = if (isProtectionOn) "停止防护" else "开启防护",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = localMessage ?: statusText(serviceState),
                style = MaterialTheme.typography.bodyLarge,
                color = when {
                    localMessage?.startsWith("启动失败") == true -> MaterialTheme.colorScheme.error
                    isProtectionOn -> MaterialTheme.colorScheme.primary
                    else -> MaterialTheme.colorScheme.onSurfaceVariant
                }
            )

            Spacer(modifier = Modifier.weight(1f))

            Text(
                text = "在视频通话中点击悬浮按钮即可截屏并运行检测",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 24.dp, vertical = 16.dp)
            )
        }
    }
}

private fun statusText(state: ServiceState): String {
    return when (state) {
        ServiceState.STOPPED -> "防护未开启"
        ServiceState.STARTING -> "启动中..."
        ServiceState.RUNNING -> "防护运行中"
        ServiceState.CAPTURE_AUTH_REQUIRED -> "需要屏幕录制授权"
        ServiceState.CAPTURING -> "正在截取屏幕..."
        ServiceState.UPLOADING -> "正在上传截图..."
        ServiceState.DETECTING -> "正在运行检测..."
        ServiceState.ERROR -> "服务异常"
    }
}
