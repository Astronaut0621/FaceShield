from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from app.algorithm.config import algorithm_settings
from app.algorithm.contracts.types import DetectionInput, DetectionOutput


RGB_MEAN = np.array([0.485, 0.456, 0.406], dtype="float32").reshape(3, 1, 1)
RGB_STD = np.array([0.229, 0.224, 0.225], dtype="float32").reshape(3, 1, 1)
FUSION_MODELS = {"fusion_fft", "fusion_v2"}


def _pil_to_rgb_tensor(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype="float32") / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    return (arr - RGB_MEAN) / RGB_STD


def _normalize_frequency_map(magnitude: np.ndarray) -> np.ndarray:
    min_value = float(magnitude.min())
    max_value = float(magnitude.max())
    if max_value > min_value:
        magnitude = (magnitude - min_value) / (max_value - min_value)
    else:
        magnitude = np.zeros_like(magnitude, dtype="float32")
    return magnitude[np.newaxis, :, :].astype("float32")


def _compute_fft_tensor(image: Image.Image) -> np.ndarray:
    gray = np.asarray(image.convert("L"), dtype="float32") / 255.0
    spectrum = np.fft.fft2(gray)
    spectrum = np.fft.fftshift(spectrum)
    magnitude = np.log1p(np.abs(spectrum)).astype("float32")
    return _normalize_frequency_map(magnitude)


def _compute_highfreq_fft_tensor(image: Image.Image, low_radius_ratio: float = 0.18) -> np.ndarray:
    gray = np.asarray(image.convert("L"), dtype="float32") / 255.0
    spectrum = np.fft.fft2(gray)
    spectrum = np.fft.fftshift(spectrum)
    magnitude = np.log1p(np.abs(spectrum)).astype("float32")
    height, width = magnitude.shape
    yy, xx = np.ogrid[:height, :width]
    cy = (height - 1) / 2.0
    cx = (width - 1) / 2.0
    radius = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    cutoff = float(radius.max()) * low_radius_ratio
    highfreq = magnitude * (radius >= cutoff).astype("float32")
    return _normalize_frequency_map(highfreq)


def _compute_frequency_tensor(image: Image.Image, mode: str) -> np.ndarray:
    if mode == "fusion_fft":
        return _compute_fft_tensor(image)
    if mode == "fusion_v2":
        return _compute_highfreq_fft_tensor(image)
    raise ValueError(f"Unsupported frequency mode: {mode}")


class PaddleDetectionEngine:
    name = "paddle"

    def __init__(self) -> None:
        self._paddle = None
        self._functional = None
        self._model = None
        self._config: dict[str, Any] | None = None

    def predict(self, payload: DetectionInput) -> DetectionOutput:
        self._ensure_loaded()
        assert self._paddle is not None
        assert self._functional is not None
        assert self._model is not None
        assert self._config is not None

        model_name = self._config.get("model", "fusion_v2")
        image_size = int(self._config.get("image_size", 224))

        image = Image.open(payload.image_path).convert("RGB")
        if image.size != (image_size, image_size):
            image = image.resize((image_size, image_size), Image.BILINEAR)

        rgb = self._paddle.to_tensor(_pil_to_rgb_tensor(image)).unsqueeze(0)
        with self._paddle.no_grad():
            if model_name in FUSION_MODELS:
                frequency = self._paddle.to_tensor(_compute_frequency_tensor(image, model_name)).unsqueeze(0)
                logits = self._model(rgb, frequency)
            else:
                logits = self._model(rgb)
            prob = self._functional.softmax(logits, axis=1).numpy()[0]

        real_probability = float(prob[0])
        fake_probability = float(prob[1])
        label = "fake" if fake_probability >= 0.5 else "real"
        confidence = max(real_probability, fake_probability)

        return DetectionOutput(
            label=label,
            fake_probability=round(fake_probability, 4),
            confidence=round(confidence, 4),
            risk_level=None,
            frequency_score=round(fake_probability, 4) if model_name in FUSION_MODELS else None,
            spatial_score=round(real_probability if label == "real" else fake_probability, 4),
            heatmap_path=None,
            heatmap_url=None,
            model_name=algorithm_settings.model_name,
            model_version=algorithm_settings.model_version,
        )

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return

        self._prepare_paddle_cache()
        try:
            import paddle
            import paddle.nn.functional as F
        except ImportError as exc:
            raise RuntimeError(
                "PaddlePaddle is required for FACESHIELD_ALGORITHM_BACKEND=paddle. "
                "Install PaddlePaddle or switch FACESHIELD_ALGORITHM_BACKEND=mock."
            ) from exc

        from app.algorithm.models.paddle_model import build_model

        config_path = Path(algorithm_settings.model_config_path or "")
        model_path = Path(algorithm_settings.model_path or "")
        if not config_path.exists():
            raise FileNotFoundError(f"Model config not found: {config_path}")
        if not model_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found: {model_path}")

        config = json.loads(config_path.read_text(encoding="utf-8"))
        model_name = config.get("model", "fusion_v2")
        dropout = float(config.get("dropout", 0.3))
        feature_dim = int(config.get("feature_dim", 128))

        paddle.set_device("gpu" if paddle.device.is_compiled_with_cuda() else "cpu")
        model = build_model(model_name, dropout=dropout, feature_dim=feature_dim)
        model.set_state_dict(paddle.load(str(model_path)))
        model.eval()

        self._paddle = paddle
        self._functional = F
        self._model = model
        self._config = config

    @staticmethod
    def _prepare_paddle_cache() -> None:
        from app.core.config import settings

        paddle_home = settings.STORAGE_DIR / "paddle_home"
        paddle_home.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("HOME", str(paddle_home))
        os.environ.setdefault("USERPROFILE", str(paddle_home))
        os.environ.setdefault("PADDLE_HOME", str(paddle_home))
