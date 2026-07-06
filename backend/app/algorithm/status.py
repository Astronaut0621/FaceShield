from __future__ import annotations

import importlib.util
from pathlib import Path

from app.algorithm.config import algorithm_settings


def get_algorithm_status() -> dict:
    model_path = Path(algorithm_settings.model_path or "")
    config_path = Path(algorithm_settings.model_config_path or "")
    paddle_available = importlib.util.find_spec("paddle") is not None
    opencv_available = importlib.util.find_spec("cv2") is not None

    ready = True
    warnings: list[str] = []
    if algorithm_settings.backend == "paddle":
        if not paddle_available:
            ready = False
            warnings.append("PaddlePaddle is not installed.")
        if not model_path.exists():
            ready = False
            warnings.append(f"Model checkpoint not found: {model_path}")
        if not config_path.exists():
            ready = False
            warnings.append(f"Model config not found: {config_path}")
    if not opencv_available:
        warnings.append("OpenCV is not installed; center crop fallback will be used.")

    return {
        "backend": algorithm_settings.backend,
        "ready": ready,
        "model_name": "FaceShield-MockNet" if algorithm_settings.backend == "mock" else algorithm_settings.model_name,
        "model_version": "v0.1" if algorithm_settings.backend == "mock" else algorithm_settings.model_version,
        "model_path": str(model_path) if algorithm_settings.model_path else None,
        "model_path_exists": model_path.exists() if algorithm_settings.model_path else False,
        "model_config_path": str(config_path) if algorithm_settings.model_config_path else None,
        "model_config_exists": config_path.exists() if algorithm_settings.model_config_path else False,
        "paddle_available": paddle_available,
        "opencv_available": opencv_available,
        "warnings": warnings,
    }
