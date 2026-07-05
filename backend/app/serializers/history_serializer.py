from app.models.detection_result import DetectionResult
from app.models.file_record import FileRecord
from app.serializers.detection_serializer import serialize_detection_result
from app.utils.time_utils import format_datetime


def serialize_history_item(result: DetectionResult, file_record: FileRecord) -> dict:
    return {
        "task_id": result.task_id,
        "file_id": result.file_id,
        "original_filename": file_record.original_filename,
        "label": result.label,
        "fake_probability": float(result.fake_probability) if result.fake_probability is not None else None,
        "risk_level": result.risk_level,
        "original_image_url": file_record.file_url,
        "heatmap_url": result.heatmap_url,
        "created_at": format_datetime(result.created_at),
    }


def serialize_history_detail(result: DetectionResult, file_record: FileRecord) -> dict:
    data = serialize_detection_result(result)
    data.update(
        {
            "original_filename": file_record.original_filename,
            "stored_filename": file_record.stored_filename,
            "file_url": file_record.file_url,
        }
    )
    return data
