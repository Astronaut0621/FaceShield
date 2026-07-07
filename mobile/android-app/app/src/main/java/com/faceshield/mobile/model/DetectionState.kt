package com.faceshield.mobile.model

import com.faceshield.mobile.model.RiskLevel

sealed class DetectionState {
    data object Idle : DetectionState()
    data object NotLoggedIn : DetectionState()
    data object CaptureAuthRequired : DetectionState()
    data object Capturing : DetectionState()
    data object Uploading : DetectionState()
    data object Detecting : DetectionState()
    data class Success(val result: DetectionResult, val riskLevel: RiskLevel) : DetectionState()
    data class Failure(val message: String) : DetectionState()
}