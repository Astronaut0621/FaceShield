package com.faceshield.mobile.model

enum class ServiceState {
    STOPPED,
    STARTING,
    RUNNING,
    CAPTURE_AUTH_REQUIRED,
    CAPTURING,
    UPLOADING,
    DETECTING,
    ERROR
}