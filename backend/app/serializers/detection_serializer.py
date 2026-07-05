from app.models.detection_result import DetectionResult
from app.utils.time_utils import format_datetime


def serialize_detection_result(result: DetectionResult) -> dict:
    return {
        "task_id": result.task_id,
        "file_id": result.file_id,
        "label": result.label,
        "fake_probability": float(result.fake_probability) if result.fake_probability is not None else None,
        "confidence": float(result.confidence) if result.confidence is not None else None,
        "risk_level": result.risk_level,
        "frequency_score": float(result.frequency_score) if result.frequency_score is not None else None,
        "spatial_score": float(result.spatial_score) if result.spatial_score is not None else None,
        "heatmap_url": result.heatmap_url,
        "face_crop_url": result.face_crop_url,
        "face_detected": result.face_detected,
        "suggestion": result.suggestion,
        "model_name": result.model_name,
        "model_version": result.model_version,
        "created_at": format_datetime(result.created_at),
    }
