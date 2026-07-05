from app.algorithm.contracts.engine import DetectionEngine
from app.algorithm.models.mock_engine import MockDetectionEngine


class EngineRegistry:
    def __init__(self):
        self._engines: dict[str, DetectionEngine] = {}

    def register(self, engine: DetectionEngine) -> None:
        self._engines[engine.name] = engine

    def get(self, name: str) -> DetectionEngine:
        try:
            return self._engines[name]
        except KeyError as exc:
            raise ValueError(f"Unknown detection engine: {name}") from exc


engine_registry = EngineRegistry()
engine_registry.register(MockDetectionEngine())

