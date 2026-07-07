from pydantic import BaseModel, Field


class DetectionStartRequest(BaseModel):
    file_id: int = Field(..., ge=1)
    model_id: int | None = Field(None, ge=1)


class DetectionReport(BaseModel):
    record_id: int | None = None
    task_id: int
    file_id: int
    label: str | None
    prediction: str | None = None
    fake_probability: float | None
    confidence: float | None
    risk_level: str | None
    frequency_score: float | None
    spatial_score: float | None
    original_filename: str | None = None
    original_image_url: str | None = None
    face_crop_url: str | None = None
    face_detected: bool | None = None
    heatmap_url: str | None
    suggestion: str | None
    model_name: str | None
    model_version: str | None
    created_at: str | None
