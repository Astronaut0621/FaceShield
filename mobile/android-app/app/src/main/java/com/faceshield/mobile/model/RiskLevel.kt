package com.faceshield.mobile.model

enum class RiskLevel(val displayName: String, val colorHex: String) {
    LOW("低风险", "#00E676"),
    MEDIUM("中风险", "#FF9100"),
    HIGH("高风险", "#F44336"),
    UNKNOWN("未知", "#9E9E9E");

    companion object {
        fun fromString(value: String?): RiskLevel = when (value?.lowercase()) {
            "low" -> LOW
            "medium" -> MEDIUM
            "high" -> HIGH
            else -> UNKNOWN
        }
    }
}
