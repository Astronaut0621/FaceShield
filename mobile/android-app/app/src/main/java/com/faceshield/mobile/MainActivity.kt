package com.faceshield.mobile

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import com.faceshield.mobile.service.FaceShieldOverlayService
import com.faceshield.mobile.ui.navigation.NavGraph
import com.faceshield.mobile.ui.theme.FaceShieldTheme

class MainActivity : ComponentActivity() {

    private val mediaProjectionLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val data = result.data
        if (result.resultCode == RESULT_OK && data != null) {
            FaceShieldOverlayService.setMediaProjectionResult(result.resultCode, data)
            ContextCompat.startForegroundService(
                this,
                Intent(this, FaceShieldOverlayService::class.java).apply {
                    action = FaceShieldOverlayService.ACTION_MEDIA_PROJECTION_READY
                }
            )
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            FaceShieldTheme {
                NavGraph(
                    onRequestMediaProjection = { requestMediaProjection() }
                )
            }
        }
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIntent(intent)
    }

    private fun requestMediaProjection() {
        val service = getSystemService(MEDIA_PROJECTION_SERVICE) as android.media.projection.MediaProjectionManager
        mediaProjectionLauncher.launch(service.createScreenCaptureIntent())
    }

    private fun handleIntent(intent: Intent?) {
        if (intent?.action == ACTION_REQUEST_MEDIA_PROJECTION) {
            requestMediaProjection()
        }
    }

    companion object {
        const val ACTION_REQUEST_MEDIA_PROJECTION = "com.faceshield.mobile.ACTION_REQUEST_MEDIA_PROJECTION"
    }
}
