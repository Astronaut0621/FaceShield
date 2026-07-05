from app.algorithm.contracts.types import DetectionInput
from app.algorithm.models.mock_engine import MockDetectionEngine


def mock_predict_image(image_path: str) -> dict:
    return MockDetectionEngine().predict(DetectionInput(image_path=image_path)).to_dict()
