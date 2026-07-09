package com.faceshield.mobile.ui.screen

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.compose.ui.platform.LocalLifecycleOwner
import com.faceshield.mobile.service.FaceShieldOverlayService

@Composable
fun PermissionGuideScreen(
    onAllPermissionsGranted: () -> Unit,
    onRequestMediaProjection: () -> Unit = {}
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    // ---------------------------------------------------------------
    // 各权限状态
    // ---------------------------------------------------------------
    var overlayGranted by remember { mutableStateOf(Settings.canDrawOverlays(context)) }
    var notificationGranted by remember {
        mutableStateOf(
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                ContextCompat.checkSelfPermission(
                    context,
                    android.Manifest.permission.POST_NOTIFICATIONS
                ) == android.content.pm.PackageManager.PERMISSION_GRANTED
            } else {
                true
            }
        )
    }
    var screenRecordGranted by remember { mutableStateOf(false) }

    // 记录用户是否主动操作过某个权限 (否认也算"已选择")
    var overlayChosen by remember { mutableStateOf(Settings.canDrawOverlays(context)) }
    var notificationChosen by remember {
        mutableStateOf(
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                ContextCompat.checkSelfPermission(
                    context,
                    android.Manifest.permission.POST_NOTIFICATIONS
                ) == android.content.pm.PackageManager.PERMISSION_GRANTED
            } else {
                true
            }
        )
    }
    var screenRecordChosen by remember { mutableStateOf(false) }

    // ---------------------------------------------------------------
    // Launcher：悬浮窗 → 跳转系统设置页
    // ---------------------------------------------------------------
    val overlayLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) {
        overlayGranted = Settings.canDrawOverlays(context)
        overlayChosen = true
    }

    // ---------------------------------------------------------------
    // Launcher：通知 → 系统权限弹窗
    // ---------------------------------------------------------------
    val notificationLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        notificationGranted = granted
        notificationChosen = true
    }

    // ---------------------------------------------------------------
    // 从系统设置页返回时刷新悬浮窗 / 通知状态，
    // 以及检查屏幕录制授权结果（通过 MainActivity 的 launcher）
    // ---------------------------------------------------------------
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                overlayGranted = Settings.canDrawOverlays(context)
                notificationGranted = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    ContextCompat.checkSelfPermission(
                        context,
                        android.Manifest.permission.POST_NOTIFICATIONS
                    ) == android.content.pm.PackageManager.PERMISSION_GRANTED
                } else {
                    true
                }
                // 检查屏幕录制授权是否刚从系统对话框返回
                if (FaceShieldOverlayService.consumeMediaProjectionJustGranted()) {
                    screenRecordGranted = true
                    screenRecordChosen = true
                }
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    val allChosen = overlayChosen && notificationChosen && screenRecordChosen

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ---- 标题 ----
        Text(
            text = "权限设置",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = "请逐一选择是否授予以下权限。您也可以稍后在系统设置中更改。",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Spacer(modifier = Modifier.height(4.dp))

        // ---- 悬浮窗 ----
        PermissionSelectionCard(
            title = "悬浮窗",
            description = "在其他应用上方显示扫描按钮",
            icon = "🟦",
            granted = overlayGranted,
            chosen = overlayChosen,
            extraHint = null,
            onToggle = {
                overlayLauncher.launch(
                    Intent(
                        Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:${context.packageName}")
                    )
                )
            }
        )

        // ---- 通知 ----
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            PermissionSelectionCard(
                title = "通知",
                description = "显示前台服务通知，确保持续运行",
                icon = "🔔",
                granted = notificationGranted,
                chosen = notificationChosen,
                extraHint = null,
                onToggle = {
                    notificationLauncher.launch(android.Manifest.permission.POST_NOTIFICATIONS)
                }
            )
        }

        // ---- 屏幕录制 ----
        PermissionSelectionCard(
            title = "屏幕录制",
            description = "截取屏幕画面并提交 AI 检测",
            icon = "📱",
            granted = screenRecordGranted,
            chosen = screenRecordChosen,
            extraHint = "需要通过系统弹窗授权",
            onToggle = {
                onRequestMediaProjection()
            }
        )

        Spacer(modifier = Modifier.weight(1f))

        // ---- 继续按钮 ----
        Button(
            onClick = onAllPermissionsGranted,
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 8.dp),
            enabled = allChosen
        ) {
            Text("继续")
        }

        Spacer(modifier = Modifier.height(16.dp))
    }
}

// =========================================================================
// 权限选择卡片 — 使用 Switch 让用户主动开启/关闭
// =========================================================================
@Composable
private fun PermissionSelectionCard(
    title: String,
    description: String,
    icon: String,
    granted: Boolean,
    chosen: Boolean,
    extraHint: String?,
    onToggle: () -> Unit
) {
    val borderColor = when {
        !chosen -> MaterialTheme.colorScheme.outlineVariant
        granted -> Color(0xFF4CAF50)
        else -> Color(0xFFE53935)
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, borderColor)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 图标
            Text(text = icon, style = MaterialTheme.typography.headlineSmall)

            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 12.dp)
            ) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = description,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                // 额外提示
                if (extraHint != null) {
                    Text(
                        text = extraHint,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.padding(top = 1.dp)
                    )
                }
                // 结果提示
                if (chosen) {
                    Text(
                        text = if (granted) "✓ 已授权" else "✗ 未授权",
                        style = MaterialTheme.typography.labelSmall,
                        color = if (granted) Color(0xFF4CAF50) else Color(0xFFE53935),
                        modifier = Modifier.padding(top = 2.dp)
                    )
                }
            }

            // Switch — 用户主动滑动选择
            Switch(
                checked = chosen && granted,
                onCheckedChange = {
                    if (!chosen || !granted) {
                        onToggle()
                    }
                },
                enabled = !chosen || !granted
            )}
    }
}
