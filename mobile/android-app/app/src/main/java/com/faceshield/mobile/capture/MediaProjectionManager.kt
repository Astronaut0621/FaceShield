package com.faceshield.mobile.capture

import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager as AndroidMediaProjectionManager
import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class MediaProjectionManager(private val context: Context) {

    private val _isAuthorized = MutableStateFlow(false)
    val isAuthorized: StateFlow<Boolean> = _isAuthorized.asStateFlow()

    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null

    private val systemMpm by lazy {
        context.getSystemService(Context.MEDIA_PROJECTION_SERVICE) as AndroidMediaProjectionManager
    }

    fun createAuthIntent(): Intent = systemMpm.createScreenCaptureIntent()

    fun onAuthResult(resultCode: Int, data: Intent) {
        recreateFromSaved(resultCode, data)
    }

    /**
     * 从之前保存的授权结果重新创建 MediaProjection 会话。
     * 授权一次后，即使系统回收或异常断开，也可静默恢复，不再弹系统对话框。
     */
    fun recreateFromSaved(resultCode: Int, data: Intent): Boolean {
        releaseVirtualDisplay()
        mediaProjection?.unregisterCallback(projectionCallback)
        mediaProjection = systemMpm.getMediaProjection(resultCode, data)
        _isAuthorized.value = mediaProjection != null

        mediaProjection?.registerCallback(projectionCallback, Handler(Looper.getMainLooper()))
        return mediaProjection != null
    }

    private val projectionCallback = object : MediaProjection.Callback() {
        override fun onStop() {
            releaseVirtualDisplay()
            _isAuthorized.value = false
            mediaProjection = null
        }
    }

    fun createVirtualDisplay(width: Int, height: Int): ImageReader? {
        val projection = mediaProjection ?: return null
        releaseVirtualDisplay()

        val reader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2)
        imageReader = reader
        virtualDisplay = projection.createVirtualDisplay(
            "FaceShieldCapture",
            width,
            height,
            context.resources.displayMetrics.densityDpi,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            reader.surface,
            null,
            null
        )
        return reader
    }

    fun releaseVirtualDisplay() {
        virtualDisplay?.release()
        virtualDisplay = null
        imageReader?.close()
        imageReader = null
    }

    fun release() {
        releaseVirtualDisplay()
        mediaProjection?.stop()
        mediaProjection = null
        _isAuthorized.value = false
    }
}
