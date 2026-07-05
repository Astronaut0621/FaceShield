from app.models.model_version import ModelVersion
from app.utils.time_utils import format_datetime


def serialize_model_version(model: ModelVersion) -> dict:
    return {
        "id": model.id,
        "model_name": model.model_name,
        "version": model.version,
        "description": model.description,
        "is_active": model.is_active,
        "created_at": format_datetime(model.created_at),
    }

