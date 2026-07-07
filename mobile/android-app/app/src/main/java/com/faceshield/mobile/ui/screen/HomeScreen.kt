package com.faceshield.mobile.ui.screen

import android.content.Intent
import android.net.Uri
import android.provider.Settings
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.collectAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
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
    val serviceState by FaceShieldOverlayService.serviceState.collectAsState()
    val isProtectionOn = serviceState != ServiceState.STOPPED
    var localMessage by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(serviceState) {
        if (serviceState == ServiceState.CAPTURE_AUTH_REQUIRED) {
            onRequestMediaProjection()
        }
    }

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = true,
                    onClick = {},
                    icon = { Text("Home") },
                    label = { Text("Home") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateToRecords,
                    icon = { Text("Log") },
                    label = { Text("Records") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateToSettings,
                    icon = { Text("Set") },
                    label = { Text("Settings") }
                )
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "FaceShield",
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = localMessage ?: statusText(serviceState),
                style = MaterialTheme.typography.bodyLarge,
                color = if (isProtectionOn) {
                    MaterialTheme.colorScheme.primary
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                }
            )

            Spacer(modifier = Modifier.height(48.dp))

            FilledTonalButton(
                onClick = {
                    if (isProtectionOn) {
                        context.startService(
                            Intent(context, FaceShieldOverlayService::class.java).apply {
                                action = FaceShieldOverlayService.ACTION_STOP
                            }
                        )
                    } else if (Settings.canDrawOverlays(context)) {
                        context.startForegroundService(Intent(context, FaceShieldOverlayService::class.java))
                        localMessage = null
                    } else {
                        localMessage = "Floating window permission is required."
                        context.startActivity(
                            Intent(
                                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                                Uri.parse("package:${context.packageName}")
                            )
                        )
                    }
                },
                modifier = Modifier.size(width = 240.dp, height = 56.dp)
            ) {
                Text(
                    text = if (isProtectionOn) "Stop protection" else "Start protection",
                    style = MaterialTheme.typography.titleMedium
                )
            }

            Spacer(modifier = Modifier.weight(1f))

            Text(
                text = "Tap the floating button during a video call to capture the screen and run detection.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

private fun statusText(state: ServiceState): String {
    return when (state) {
        ServiceState.STOPPED -> "Protection is off"
        ServiceState.STARTING -> "Starting..."
        ServiceState.RUNNING -> "Protection is running"
        ServiceState.CAPTURE_AUTH_REQUIRED -> "Screen capture authorization required"
        ServiceState.CAPTURING -> "Capturing screen..."
        ServiceState.UPLOADING -> "Uploading screenshot..."
        ServiceState.DETECTING -> "Running detection..."
        ServiceState.ERROR -> "Service error"
    }
}
