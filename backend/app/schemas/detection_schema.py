from pydantic import BaseModel, Field


class DetectionStartRequest(BaseModel):
    file_id: int = Field(..., ge=1)


class DetectionReport(BaseModel):
    task_id: int
    file_id: int
    label: str | None
    fake_probability: float | None
    confidence: float | None
    risk_level: str | None
    frequency_score: float | None
    spatial_score: float | None
    heatmap_url: str | None
    suggestion: str | None
    model_name: str | None
    model_version: str | None
    created_at: str | None

