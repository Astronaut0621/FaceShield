from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from urllib.parse import urlparse
from uuid import uuid4

import numpy as np
from PIL import Image, ImageFilter


@dataclass(frozen=True)
class HeatmapResult:
    heatmap_path: str | None
    heatmap_url: str


def build_heatmap_url(
    heatmap_path: str | None,
    storage_dir: str | Path,
    output_url_prefix: str = "/storage/heatmaps",
    source_roots: list[str | Path] | tuple[str | Path, ...] | None = None,
) -> str | None:
    result = prepare_heatmap_artifact(
        heatmap_path,
        output_dir=storage_dir,
        output_url_prefix=output_url_prefix,
        source_roots=source_roots,
    )
    return result.heatmap_url if result else None


def prepare_heatmap_artifact(
    heatmap_ref: str | None,
    output_dir: str | Path,
    output_url_prefix: str = "/storage/heatmaps",
    source_roots: list[str | Path] | tuple[str | Path, ...] | None = None,
) -> HeatmapResult | None:
    if not heatmap_ref:
        return None

    normalized_ref = str(heatmap_ref).strip()
    if not normalized_ref:
        return None

    parsed = urlparse(normalized_ref)
    if parsed.scheme in {"http", "https"}:
        return HeatmapResult(heatmap_path=None, heatmap_url=normalized_ref)

    if normalized_ref.startswith("/storage/"):
        return HeatmapResult(heatmap_path=None, heatmap_url=normalized_ref)

    if normalized_ref.startswith("storage/"):
        return HeatmapResult(heatmap_path=None, heatmap_url=f"/{normalized_ref}")

    source_path = _resolve_existing_file(normalized_ref, source_roots)
    if not source_path.exists() or not source_path.is_file():
        return None

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        relative = source_path.resolve().relative_to(output_path.resolve())
        return HeatmapResult(
            heatmap_path=str(source_path),
            heatmap_url=f"{output_url_prefix.rstrip('/')}/{relative.as_posix()}",
        )
    except ValueError:
        pass

    suffix = source_path.suffix or ".png"
    target_name = f"{source_path.stem}_{uuid4().hex[:12]}{suffix}"
    target_path = output_path / target_name
    shutil.copy2(source_path, target_path)
    return HeatmapResult(
        heatmap_path=str(target_path),
        heatmap_url=f"{output_url_prefix.rstrip('/')}/{target_name}",
    )


def _resolve_existing_file(
    file_ref: str,
    source_roots: list[str | Path] | tuple[str | Path, ...] | None = None,
) -> Path:
    source_path = Path(file_ref)
    if source_path.exists() or source_path.is_absolute():
        return source_path

    for root in source_roots or ():
        candidate = Path(root) / file_ref
        if candidate.exists():
            return candidate

    return source_path


def generate_fallback_heatmap(
    image_path: str,
    output_dir: str | Path,
    output_url_prefix: str = "/storage/heatmaps",
) -> HeatmapResult:
    source_path = Path(image_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    image = Image.open(source_path).convert("RGB")
    heatmap_image = build_fallback_heatmap_image(image)
    filename = f"{source_path.stem}_{uuid4().hex[:12]}.png"
    heatmap_file = output_path / filename
    heatmap_image.save(heatmap_file)

    return HeatmapResult(
        heatmap_path=str(heatmap_file),
        heatmap_url=f"{output_url_prefix}/{filename}",
    )


def build_fallback_heatmap_image(image: Image.Image) -> Image.Image:
    gray_image = image.convert("L")
    gray = np.asarray(gray_image, dtype="float32") / 255.0

    edge_image = gray_image.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(radius=1.4))
    edge = np.asarray(edge_image, dtype="float32") / 255.0

    smooth_image = gray_image.filter(ImageFilter.GaussianBlur(radius=5))
    smooth = np.asarray(smooth_image, dtype="float32") / 255.0
    local_contrast = np.abs(gray - smooth)

    height, width = gray.shape
    yy, xx = np.mgrid[0:height, 0:width]
    cy = (height - 1) / 2.0
    cx = (width - 1) / 2.0
    radius = np.sqrt(((yy - cy) / max(cy, 1.0)) ** 2 + ((xx - cx) / max(cx, 1.0)) ** 2)
    center_prior = np.clip(1.0 - radius, 0.0, 1.0)

    saliency = 0.50 * _normalize(edge) + 0.34 * _normalize(local_contrast) + 0.16 * center_prior
    saliency = _contrast_stretch(saliency, low_percentile=12, high_percentile=96)
    saliency = np.power(saliency, 0.62)
    saliency = np.asarray(
        Image.fromarray((saliency * 255).astype("uint8"), mode="L")
        .filter(ImageFilter.GaussianBlur(radius=2.4)),
        dtype="float32",
    ) / 255.0
    saliency = _contrast_stretch(saliency, low_percentile=6, high_percentile=94)

    heatmap = _colorize(saliency)
    return Image.fromarray(heatmap, mode="RGBA")


def _normalize(values: np.ndarray) -> np.ndarray:
    min_value = float(values.min())
    max_value = float(values.max())
    if max_value <= min_value:
        return np.zeros_like(values, dtype="float32")
    return (values - min_value) / (max_value - min_value)


def _contrast_stretch(
    values: np.ndarray,
    low_percentile: float = 5,
    high_percentile: float = 95,
) -> np.ndarray:
    low = float(np.percentile(values, low_percentile))
    high = float(np.percentile(values, high_percentile))
    if high <= low:
        return _normalize(values)
    return ((values - low) / (high - low)).clip(0.0, 1.0)


def _colorize(values: np.ndarray) -> np.ndarray:
    values = values.clip(0.0, 1.0)
    alpha = (120 + values * 85).clip(120, 205).astype("uint8")
    red = (np.clip(1.85 * values - 0.18, 0.0, 1.0) * 245).astype("uint8")
    green = ((1.0 - np.abs(values - 0.55) * 1.65).clip(0.0, 1.0) * 220).astype("uint8")
    blue = (np.clip(1.02 - 1.65 * values, 0.0, 1.0) * 230).astype("uint8")
    return np.stack([red, green, blue, alpha], axis=-1)
