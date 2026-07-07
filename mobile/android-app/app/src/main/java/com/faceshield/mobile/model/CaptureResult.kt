package com.faceshield.mobile.model

import java.io.File

sealed class CaptureResult {
    data class Success(val file: File) : CaptureResult()
    data object EmptyFrame : CaptureResult()
    data object BlockedBySystem : CaptureResult()
    data object NotAuthorized : CaptureResult()
    data object ProjectionSessionLost : CaptureResult()
}