from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from app.algorithm.config import algorithm_settings


def get_algorithm_status() -> dict:
    model_path = Path(algorithm_settings.model_path or "")
    config_path = Path(algorithm_settings.model_config_path or "")
    paddle_available = importlib.util.find_spec("paddle") is not None
    opencv_status = _get_opencv_status()
    opencv_available = bool(opencv_status["available"])

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
    elif not opencv_status["haar_available"]:
        warnings.append("OpenCV is installed but Haar Cascade face detection is unavailable; center crop fallback will be used.")

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
        "opencv_version": opencv_status["version"],
        "opencv_haar_available": opencv_status["haar_available"],
        "warnings": warnings,
    }


def _get_opencv_status() -> dict[str, Any]:
    if importlib.util.find_spec("cv2") is None:
        return {
            "available": False,
            "version": None,
            "haar_available": False,
        }

    try:
        import cv2
    except Exception:
        return {
            "available": False,
            "version": None,
            "haar_available": False,
        }

    cascade_path = None
    if hasattr(cv2, "data"):
        cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"

    return {
        "available": True,
        "version": getattr(cv2, "__version__", None),
        "haar_available": bool(
            hasattr(cv2, "CascadeClassifier")
            and cascade_path is not None
            and cascade_path.exists()
        ),
    }
