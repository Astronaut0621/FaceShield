package com.faceshield.mobile.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import com.faceshield.mobile.FaceShieldApp
import com.faceshield.mobile.MainActivity
import com.faceshield.mobile.auth.AuthRepository
import com.faceshield.mobile.auth.CurrentUserSession
import com.faceshield.mobile.capture.MediaProjectionManager
import com.faceshield.mobile.capture.ScreenCaptureEngine
import com.faceshield.mobile.detection.DetectionOrchestrator
import com.faceshield.mobile.detection.DetectionRepository
import com.faceshield.mobile.model.DetectionState
import com.faceshield.mobile.model.OverlayState
import com.faceshield.mobile.model.RiskLevel
import com.faceshield.mobile.model.ServiceState
import com.faceshield.mobile.network.ServerUrl
import com.faceshield.mobile.overlay.OverlayStateManager
import com.faceshield.mobile.overlay.OverlayView
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.launch

class FaceShieldOverlayService : Service() {

    companion object {
        private const val TAG = "FaceShieldOverlaySvc"
        const val CHANNEL_ID = "faceshield_overlay_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_STOP = "com.faceshield.mobile.ACTION_STOP_PROTECTION"
        const val ACTION_MEDIA_PROJECTION_READY = "com.faceshield.mobile.ACTION_MEDIA_PROJECTION_READY"

        private val _serviceState = MutableStateFlow(ServiceState.STOPPED)
        val serviceState: StateFlow<ServiceState> = _serviceState.asStateFlow()

        // 启动失败时的详细原因，供 HomeScreen 显示
        private val _startError = MutableStateFlow<String?>(null)
        val startError: StateFlow<String?> = _startError.asStateFlow()

        private var mediaProjectionResultCode: Int = 0
        private var mediaProjectionResultData: Intent? = null

        // PermissionGuideScreen 查询屏幕录制授权结果用
        private var _mediaProjectionJustGranted = false
        fun consumeMediaProjectionJustGranted(): Boolean {
            val v = _mediaProjectionJustGranted
            _mediaProjectionJustGranted = false
            return v
        }

        fun setMediaProjectionResult(resultCode: Int, data: Intent) {
            mediaProjectionResultCode = resultCode
            mediaProjectionResultData = Intent(data)
            _mediaProjectionJustGranted = true
            _serviceState.value = ServiceState.RUNNING
        }
    }

    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    private lateinit var overlayStateManager: OverlayStateManager
    private lateinit var overlayView: OverlayView
    private lateinit var mediaProjectionManager: MediaProjectionManager
    private lateinit var detectionOrchestrator: DetectionOrchestrator

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        initializeWorkflow()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            if (intent?.action == ACTION_STOP) {
                stopProtection()
                return START_NOT_STICKY
            }

            _serviceState.value = ServiceState.STARTING
            startOverlayForeground("点击悬浮按钮进行扫描")

            // 处理已获得的 MediaProjection 授权结果
            if (intent?.action == ACTION_MEDIA_PROJECTION_READY || mediaProjectionResultData != null) {
                startMediaProjectionForeground("已获取屏幕录制授权")
                consumePendingProjectionResult()
            }

            if (!overlayView.show()) {
                overlayStateManager.transitionTo(OverlayState.FAILURE)
                _serviceState.value = ServiceState.ERROR
                _startError.value = "悬浮窗无法显示：请检查系统设置中已允许「显示悬浮窗」权限"
                updateNotificationText("悬浮窗无法显示")
                return START_NOT_STICKY
            }

            _serviceState.value = ServiceState.RUNNING
            _startError.value = null

            // 已授权则直接就绪，否则等用户点击悬浮窗时再授权
            if (mediaProjectionManager.isAuthorized.value) {
                overlayStateManager.transitionTo(OverlayState.IDLE)
            } else {
                overlayStateManager.transitionTo(OverlayState.IDLE)
            }
        } catch (e: Exception) {
            Log.e(TAG, "onStartCommand 异常", e)
            _serviceState.value = ServiceState.ERROR
            _startError.value = "服务启动失败: ${e.localizedMessage}"
            updateNotificationText("服务启动失败: ${e.localizedMessage}")
        }
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        if (::overlayView.isInitialized) overlayView.hide()
        if (::mediaProjectionManager.isInitialized) mediaProjectionManager.release()
        serviceScope.cancel()
        _serviceState.value = ServiceState.STOPPED
        super.onDestroy()
    }

    private fun initializeWorkflow() {
        val app = applicationContext as FaceShieldApp
        val tokenStore = app.apiClient.authTokenStore

        overlayStateManager = OverlayStateManager(serviceScope)
        mediaProjectionManager = MediaProjectionManager(this)

        // 立即创建 DetectionOrchestrator，不依赖网络
        // captureEngine 和 basic repo 不需要登录也能工作
        val captureEngine = ScreenCaptureEngine(this@FaceShieldOverlayService, mediaProjectionManager)
        val defaultApi = app.apiClient.getApi(ServerUrl.DEFAULT)
        detectionOrchestrator = DetectionOrchestrator(
            captureEngine = captureEngine,
            detectionRepository = DetectionRepository(defaultApi),
            currentUserSession = CurrentUserSession(AuthRepository(defaultApi, tokenStore)),
            mediaProjectionManager = mediaProjectionManager
        )

        // 异步：完善 API 地址和登录会话
        serviceScope.launch {
            runCatching {
                val serverUrl = tokenStore.serverUrl.firstOrNull().orEmpty()
                val api = app.apiClient.getApi(ServerUrl.normalizeOrDefault(serverUrl))
                val authRepository = AuthRepository(api, tokenStore)
                app.apiClient.setAuthRepository(authRepository)
                val authenticatedApi = app.apiClient.getApi(ServerUrl.normalizeOrDefault(serverUrl))
                val currentUserSession = CurrentUserSession(authRepository)
                currentUserSession.refresh()

                detectionOrchestrator = DetectionOrchestrator(
                    captureEngine = captureEngine,
                    detectionRepository = DetectionRepository(authenticatedApi),
                    currentUserSession = currentUserSession,
                    mediaProjectionManager = mediaProjectionManager
                )
            }.onFailure { e ->
                Log.e(TAG, "移动端工作流初始化失败（不影响悬浮窗显示）", e)
            }
        }

        overlayView = OverlayView(
            context = this,
            stateFlow = overlayStateManager.state,
            onClick = { onOverlayClicked() },
            onLongClick = { stopProtection() }
        )

        observeOverlayState()
    }

    private fun onOverlayClicked() {
        if (detectionOrchestrator.isCurrentlyDetecting()) return

        // 每次点击都检查授权，未授权则弹出系统对话框
        if (!mediaProjectionManager.isAuthorized.value) {
            if (!consumePendingProjectionResult()) {
                overlayStateManager.transitionTo(OverlayState.PERMISSION_REQUIRED)
                _serviceState.value = ServiceState.CAPTURE_AUTH_REQUIRED
                openMediaProjectionRequest()
                return
            }
        }

        serviceScope.launch {
            detectionOrchestrator.triggerDetection().collect { state ->
                when (state) {
                    DetectionState.Idle -> overlayStateManager.transitionTo(OverlayState.IDLE)
                    DetectionState.NotLoggedIn -> {
                        overlayStateManager.transitionTo(OverlayState.FAILURE)
                        overlayStateManager.resetAfterDelay()
                    }
                    DetectionState.CaptureAuthRequired -> {
                        overlayStateManager.transitionTo(OverlayState.PERMISSION_REQUIRED)
                        _serviceState.value = ServiceState.CAPTURE_AUTH_REQUIRED
                        openMediaProjectionRequest()
                    }
                    DetectionState.Capturing -> {
                        overlayStateManager.transitionTo(OverlayState.CAPTURING)
                        _serviceState.value = ServiceState.CAPTURING
                    }
                    DetectionState.Uploading -> {
                        overlayStateManager.transitionTo(OverlayState.UPLOADING)
                        _serviceState.value = ServiceState.UPLOADING
                    }
                    DetectionState.Detecting -> {
                        overlayStateManager.transitionTo(OverlayState.DETECTING)
                        _serviceState.value = ServiceState.DETECTING
                    }
                    is DetectionState.Success -> {
                        overlayStateManager.transitionTo(state.riskLevel.toOverlayState())
                        _serviceState.value = ServiceState.RUNNING
                        overlayStateManager.resetAfterDelay()
                    }
                    is DetectionState.Failure -> {
                        overlayStateManager.transitionTo(OverlayState.FAILURE)
                        _serviceState.value = ServiceState.ERROR
                        overlayStateManager.resetAfterDelay()
                    }
                }
            }
            // 检测结束后释放授权并清除保存数据，确保下次点击重新弹系统授权框
            mediaProjectionManager.release()
            mediaProjectionResultData = null
            _serviceState.value = ServiceState.RUNNING
        }
    }

    private fun consumePendingProjectionResult(): Boolean {
        val data = mediaProjectionResultData ?: return false
        mediaProjectionManager.onAuthResult(mediaProjectionResultCode, data)
        // 不 null mediaProjectionResultData —— 永久保存授权数据，
        // 后续若系统回收 MediaProjection 可静默恢复，不再重复弹框
        return mediaProjectionManager.isAuthorized.value
    }

    private fun openMediaProjectionRequest() {
        val intent = Intent(this, MainActivity::class.java).apply {
            action = MainActivity.ACTION_REQUEST_MEDIA_PROJECTION
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP)
        }
        startActivity(intent)
    }

    private fun observeOverlayState() {
        serviceScope.launch {
            overlayStateManager.state.collect { state ->
                updateNotificationText(
                    when (state) {
                        OverlayState.IDLE -> "点击悬浮按钮进行扫描"
                        OverlayState.PERMISSION_REQUIRED -> "需要屏幕录制授权"
                        OverlayState.CAPTURING -> "正在截取屏幕..."
                        OverlayState.UPLOADING -> "正在上传截图..."
                        OverlayState.DETECTING -> "正在运行 AI 检测..."
                        OverlayState.SUCCESS_LOW -> "检测到低风险"
                        OverlayState.SUCCESS_MEDIUM -> "检测到中风险"
                        OverlayState.SUCCESS_HIGH -> "检测到高风险"
                        OverlayState.FAILURE -> "检测失败"
                    }
                )
            }
        }
    }

    private fun stopProtection() {
        if (::overlayView.isInitialized) overlayView.hide()
        if (::mediaProjectionManager.isInitialized) mediaProjectionManager.release()
        _serviceState.value = ServiceState.STOPPED
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "FaceShield 防护",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "FaceShield 悬浮检测服务"
        }
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.createNotificationChannel(channel)
    }

    private fun createNotification(text: String): Notification {
        val openPending = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val stopPending = PendingIntent.getService(
            this,
            1,
            Intent(this, FaceShieldOverlayService::class.java).apply { action = ACTION_STOP },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("FaceShield 防护运行中")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setContentIntent(openPending)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "停止", stopPending)
            .setOngoing(true)
            .build()
    }

    private fun startOverlayForeground(text: String) {
        val notification = createNotification(text)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun startMediaProjectionForeground(text: String) {
        val notification = createNotification(text)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE or
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            )
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    private fun updateNotificationText(text: String) {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, createNotification(text))
    }

    private fun RiskLevel.toOverlayState(): OverlayState {
        return when (this) {
            RiskLevel.LOW -> OverlayState.SUCCESS_LOW
            RiskLevel.MEDIUM -> OverlayState.SUCCESS_MEDIUM
            RiskLevel.HIGH -> OverlayState.SUCCESS_HIGH
            RiskLevel.UNKNOWN -> OverlayState.FAILURE
        }
    }
}
