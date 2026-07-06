from app.models.detection_result import DetectionResult
from app.models.file_record import FileRecord
from app.serializers.detection_serializer import serialize_detection_result
from app.utils.time_utils import format_datetime


def serialize_history_item(result: DetectionResult, file_record: FileRecord) -> dict:
    return {
        "record_id": result.task_id,
        "task_id": result.task_id,
        "file_id": result.file_id,
        "original_filename": file_record.original_filename,
        "original_image_url": file_record.file_url,
        "label": result.label,
        "prediction": result.label,
        "fake_probability": float(result.fake_probability) if result.fake_probability is not None else None,
        "confidence": float(result.confidence) if result.confidence is not None else None,
        "risk_level": result.risk_level,
        "face_crop_url": result.face_crop_url,
        "face_detected": result.face_detected,
        "heatmap_url": result.heatmap_url,
        "frequency_score": float(result.frequency_score) if result.frequency_score is not None else None,
        "spatial_score": float(result.spatial_score) if result.spatial_score is not None else None,
        "model_name": result.model_name,
        "model_version": result.model_version,
        "created_at": format_datetime(result.created_at),
    }


def serialize_history_detail(result: DetectionResult, file_record: FileRecord) -> dict:
    data = serialize_detection_result(result, file_record)
    data.update(
        {
            "original_filename": file_record.original_filename,
            "stored_filename": file_record.stored_filename,
            "file_url": file_record.file_url,
        }
    )
    return data
