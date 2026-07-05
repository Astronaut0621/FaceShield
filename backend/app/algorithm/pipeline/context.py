from dataclasses import dataclass, field
from typing import Any

from app.algorithm.contracts.types import DetectionInput, DetectionOutput


@dataclass
class DetectionContext:
    payload: DetectionInput
    image_data: Any = None
    features: dict[str, Any] = field(default_factory=dict)
    output: DetectionOutput | None = None

