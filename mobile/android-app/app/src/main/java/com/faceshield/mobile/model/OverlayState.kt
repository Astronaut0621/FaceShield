package com.faceshield.mobile.model

enum class OverlayState {
    IDLE,
    PERMISSION_REQUIRED,
    CAPTURING,
    UPLOADING,
    DETECTING,
    SUCCESS_LOW,
    SUCCESS_MEDIUM,
    SUCCESS_HIGH,
    FAILURE
}