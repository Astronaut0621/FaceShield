package com.faceshield.mobile.model

enum class RiskLevel(val displayName: String, val colorHex: String) {
    LOW("Low risk", "#4CAF50"),
    MEDIUM("Medium risk", "#FF9800"),
    HIGH("High risk", "#F44336"),
    UNKNOWN("Unknown", "#9E9E9E");

    companion object {
        fun fromString(value: String?): RiskLevel = when (value?.lowercase()) {
            "low" -> LOW
            "medium" -> MEDIUM
            "high" -> HIGH
            else -> UNKNOWN
        }
    }
}
