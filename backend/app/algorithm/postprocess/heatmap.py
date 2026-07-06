from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image, ImageFilter


@dataclass(frozen=True)
class HeatmapResult:
    heatmap_path: str
    heatmap_url: str


def build_heatmap_url(heatmap_path: str | None) -> str | None:
    return heatmap_path


def generate_fallback_heatmap(
    image_path: str,
    output_dir: str | Path,
    output_url_prefix: str = "/storage/heatmaps",
) -> HeatmapResult:
    source_path = Path(image_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    image = Image.open(source_path).convert("RGB")
    gray = image.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(radius=2))
    edge = np.asarray(gray, dtype="float32")
    edge = _normalize(edge)

    heatmap = _colorize(edge)
    heatmap_image = Image.fromarray(heatmap, mode="RGBA")
    filename = f"{source_path.stem}_{uuid4().hex[:12]}.png"
    heatmap_file = output_path / filename
    heatmap_image.save(heatmap_file)

    return HeatmapResult(
        heatmap_path=str(heatmap_file),
        heatmap_url=f"{output_url_prefix}/{filename}",
    )


def _normalize(values: np.ndarray) -> np.ndarray:
    min_value = float(values.min())
    max_value = float(values.max())
    if max_value <= min_value:
        return np.zeros_like(values, dtype="float32")
    return (values - min_value) / (max_value - min_value)


def _colorize(values: np.ndarray) -> np.ndarray:
    alpha = (values * 180).clip(0, 180).astype("uint8")
    red = (values * 255).clip(0, 255).astype("uint8")
    green = ((1.0 - np.abs(values - 0.55) * 1.8).clip(0, 1) * 180).astype("uint8")
    blue = ((1.0 - values) * 60).clip(0, 60).astype("uint8")
    return np.stack([red, green, blue, alpha], axis=-1)
