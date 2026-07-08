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
import android.provider.Settings
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
        const val CHANNEL_ID = "faceshield_overlay_channel"
        const val NOTIFICATION_ID = 1001
        const val ACTION_STOP = "com.faceshield.mobile.ACTION_STOP_PROTECTION"
        const val ACTION_MEDIA_PROJECTION_READY = "com.faceshield.mobile.ACTION_MEDIA_PROJECTION_READY"

        private val _serviceState = MutableStateFlow(ServiceState.STOPPED)
        val serviceState: StateFlow<ServiceState> = _serviceState.asStateFlow()

        private var mediaProjectionResultCode: Int = 0
        private var mediaProjectionResultData: Intent? = null

        fun setMediaProjectionResult(resultCode: Int, data: Intent) {
            mediaProjectionResultCode = resultCode
            mediaProjectionResultData = Intent(data)
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
        if (intent?.action == ACTION_STOP) {
            stopProtection()
            return START_NOT_STICKY
        }

        _serviceState.value = ServiceState.STARTING
        startOverlayForeground("Tap the floating button to scan.")

        if (!Settings.canDrawOverlays(this)) {
            overlayStateManager.transitionTo(OverlayState.PERMISSION_REQUIRED)
            _serviceState.value = ServiceState.ERROR
            updateNotificationText("Overlay permission is required.")
            return START_NOT_STICKY
        }

        if (intent?.action == ACTION_MEDIA_PROJECTION_READY || mediaProjectionResultData != null) {
            startMediaProjectionForeground("Screen capture authorization received.")
        }
        consumePendingProjectionResult()
        if (intent?.action == ACTION_MEDIA_PROJECTION_READY) {
            overlayStateManager.transitionTo(OverlayState.IDLE)
        }
        if (!overlayView.show()) {
            overlayStateManager.transitionTo(OverlayState.FAILURE)
            _serviceState.value = ServiceState.ERROR
            updateNotificationText("Floating window could not be shown.")
            return START_NOT_STICKY
        }
        _serviceState.value = ServiceState.RUNNING
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
                    captureEngine = ScreenCaptureEngine(this@FaceShieldOverlayService, mediaProjectionManager),
                    detectionRepository = DetectionRepository(authenticatedApi),
                    currentUserSession = currentUserSession,
                    mediaProjectionManager = mediaProjectionManager
                )
            }.onFailure {
                overlayStateManager.transitionTo(OverlayState.FAILURE)
                _serviceState.value = ServiceState.ERROR
                updateNotificationText("Mobile workflow initialization failed.")
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
        if (!::detectionOrchestrator.isInitialized) {
            overlayStateManager.transitionTo(OverlayState.FAILURE)
            overlayStateManager.resetAfterDelay()
            return
        }
        if (detectionOrchestrator.isCurrentlyDetecting()) return

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
        }
    }

    private fun consumePendingProjectionResult(): Boolean {
        val data = mediaProjectionResultData ?: return false
        mediaProjectionManager.onAuthResult(mediaProjectionResultCode, data)
        mediaProjectionResultData = null
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
                        OverlayState.IDLE -> "Tap the floating button to scan."
                        OverlayState.PERMISSION_REQUIRED -> "Screen capture authorization is required."
                        OverlayState.CAPTURING -> "Capturing screen..."
                        OverlayState.UPLOADING -> "Uploading screenshot..."
                        OverlayState.DETECTING -> "Running AI detection..."
                        OverlayState.SUCCESS_LOW -> "Low risk detected."
                        OverlayState.SUCCESS_MEDIUM -> "Medium risk detected."
                        OverlayState.SUCCESS_HIGH -> "High risk detected."
                        OverlayState.FAILURE -> "Detection failed."
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
            "FaceShield protection",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "FaceShield floating detection service"
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
            .setContentTitle("FaceShield protection is running")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setContentIntent(openPending)
            .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Stop", stopPending)
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
