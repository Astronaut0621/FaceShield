from app.algorithm.contracts.engine import DetectionEngine
from app.algorithm.contracts.types import DetectionInput, DetectionOutput
from app.algorithm.pipeline.context import DetectionContext
from app.algorithm.pipeline.stages import (
    FeatureExtractionStage,
    InferenceStage,
    PostprocessStage,
    PreprocessStage,
    ValidationStage,
)


class DetectionPipeline:
    def __init__(self, engine: DetectionEngine):
        self.stages = [
            ValidationStage(),
            PreprocessStage(),
            FeatureExtractionStage(),
            InferenceStage(engine),
            PostprocessStage(),
        ]

    def run(self, payload: DetectionInput) -> DetectionOutput:
        context = DetectionContext(payload=payload)
        for stage in self.stages:
            context = stage.run(context)
        if context.output is None:
            raise RuntimeError("Detection pipeline did not produce output.")
        return context.output

