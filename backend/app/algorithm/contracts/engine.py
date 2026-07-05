from typing import Protocol

from app.algorithm.contracts.types import DetectionInput, DetectionOutput


class DetectionEngine(Protocol):
    name: str

    def predict(self, payload: DetectionInput) -> DetectionOutput:
        ...

