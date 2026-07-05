from enum import Enum


class DetectionLabel(str, Enum):
    REAL = "real"
    FAKE = "fake"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class TaskType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
