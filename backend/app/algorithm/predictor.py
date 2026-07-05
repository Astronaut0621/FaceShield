from pathlib import Path

from app.algorithm.config import algorithm_settings
from app.algorithm.contracts.types import DetectionInput
from app.algorithm.models.registry import engine_registry
from app.algorithm.pipeline import DetectionPipeline


def predict_image(image_path: str) -> dict:
    path = Path(image_path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    engine = engine_registry.get(algorithm_settings.backend)
    output = DetectionPipeline(engine).run(DetectionInput(image_path=str(path)))
    return output.to_dict()
