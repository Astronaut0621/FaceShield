import hashlib
import random

from app.algorithm.config import algorithm_settings
from app.algorithm.contracts.types import DetectionInput, DetectionOutput


class MockDetectionEngine:
    name = "mock"

    def predict(self, payload: DetectionInput) -> DetectionOutput:
        digest = hashlib.sha256(payload.image_path.encode("utf-8")).hexdigest()
        rng = random.Random(int(digest[:16], 16))

        fake_probability = round(rng.uniform(0.08, 0.94), 4)
        confidence = round(rng.uniform(0.72, 0.98), 4)
        frequency_score = round(min(0.99, max(0.01, fake_probability + rng.uniform(-0.12, 0.12))), 4)
        spatial_score = round(min(0.99, max(0.01, fake_probability + rng.uniform(-0.15, 0.15))), 4)
        label = "fake" if fake_probability >= 0.5 else "real"

        return DetectionOutput(
            label=label,
            fake_probability=fake_probability,
            confidence=confidence,
            risk_level=None,
            frequency_score=frequency_score,
            spatial_score=spatial_score,
            heatmap_path=None,
            model_name=algorithm_settings.model_name,
            model_version=algorithm_settings.model_version,
        )

