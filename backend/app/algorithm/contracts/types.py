from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionInput:
    image_path: str
    request_id: str | None = None


@dataclass(frozen=True)
class DetectionOutput:
    label: str
    fake_probability: float
    confidence: float
    risk_level: str | None
    frequency_score: float | None
    spatial_score: float | None
    heatmap_path: str | None
    heatmap_url: str | None
    model_name: str
    model_version: str

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "fake_probability": self.fake_probability,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "frequency_score": self.frequency_score,
            "spatial_score": self.spatial_score,
            "heatmap_path": self.heatmap_path,
            "heatmap_url": self.heatmap_url,
            "model_name": self.model_name,
            "model_version": self.model_version,
        }
