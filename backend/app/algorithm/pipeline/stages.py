from app.algorithm.contracts.engine import DetectionEngine
from app.algorithm.pipeline.context import DetectionContext


class ValidationStage:
    def run(self, context: DetectionContext) -> DetectionContext:
        if not context.payload.image_path:
            raise ValueError("image_path is required.")
        return context


class PreprocessStage:
    def run(self, context: DetectionContext) -> DetectionContext:
        return context


class FeatureExtractionStage:
    def run(self, context: DetectionContext) -> DetectionContext:
        context.features.setdefault("frequency", None)
        context.features.setdefault("spatial", None)
        return context


class InferenceStage:
    def __init__(self, engine: DetectionEngine):
        self.engine = engine

    def run(self, context: DetectionContext) -> DetectionContext:
        context.output = self.engine.predict(context.payload)
        return context


class PostprocessStage:
    def run(self, context: DetectionContext) -> DetectionContext:
        return context

