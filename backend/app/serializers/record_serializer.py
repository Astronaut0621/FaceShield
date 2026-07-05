from app.models.detection_result import DetectionResult
from app.models.file_record import FileRecord
from app.utils.time_utils import format_datetime


def serialize_detection_record(result: DetectionResult, file_record: FileRecord) -> dict:
    return {
        "record_id": result.task_id,
        "prediction": result.label,
        "fake_probability": float(result.fake_probability) if result.fake_probability is not None else None,
        "risk_level": result.risk_level,
        "original_image_url": file_record.file_url,
        "face_crop_url": result.face_crop_url,
        "heatmap_url": result.heatmap_url,
        "created_at": format_datetime(result.created_at),
    }

