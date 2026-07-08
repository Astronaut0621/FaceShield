package com.faceshield.mobile.detection

import com.faceshield.mobile.auth.CurrentUserSession
import com.faceshield.mobile.capture.MediaProjectionManager
import com.faceshield.mobile.capture.ScreenCaptureEngine
import com.faceshield.mobile.model.CaptureResult
import com.faceshield.mobile.model.DetectionState
import com.faceshield.mobile.model.NetworkResult
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.util.concurrent.atomic.AtomicBoolean

class DetectionOrchestrator(
    private val captureEngine: ScreenCaptureEngine,
    private val detectionRepository: DetectionRepository,
    private val currentUserSession: CurrentUserSession,
    private val mediaProjectionManager: MediaProjectionManager
) {

    private val isDetecting = AtomicBoolean(false)

    fun triggerDetection(): Flow<DetectionState> = flow {
        if (!isDetecting.compareAndSet(false, true)) return@flow

        try {
            currentUserSession.refresh()
            if (!currentUserSession.isLoggedIn.value) {
                emit(DetectionState.NotLoggedIn)
                return@flow
            }

            if (!mediaProjectionManager.isAuthorized.value) {
                emit(DetectionState.CaptureAuthRequired)
                return@flow
            }

            emit(DetectionState.Capturing)
            when (val captureResult = captureEngine.captureScreen()) {
                is CaptureResult.Success -> {
                    emit(DetectionState.Uploading)
                    when (val detectResult = detectionRepository.detect(captureResult.file)) {
                        is NetworkResult.Success -> {
                            val result = detectResult.data
                            emit(DetectionState.Success(result, result.riskLevel))
                        }

                        is NetworkResult.Error -> {
                            if (detectResult.code == 401) currentUserSession.clear()
                            emit(DetectionState.Failure(detectResult.message))
                        }

                        is NetworkResult.Exception -> {
                            emit(DetectionState.Failure("Detection failed. Please try again."))
                        }
                    }
                    captureResult.file.delete()
                }

                CaptureResult.EmptyFrame -> emit(DetectionState.Failure("Current screen could not be captured."))
                CaptureResult.BlockedBySystem -> emit(DetectionState.Failure("Capture is blocked by the system."))
                CaptureResult.NotAuthorized,
                CaptureResult.ProjectionSessionLost -> emit(DetectionState.CaptureAuthRequired)
            }
        } finally {
            isDetecting.set(false)
        }
    }

    fun isCurrentlyDetecting(): Boolean = isDetecting.get()
}
