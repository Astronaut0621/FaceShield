from __future__ import annotations

import csv
import random
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance
import paddle


RGB_MEAN = np.array([0.485, 0.456, 0.406], dtype="float32").reshape(3, 1, 1)
RGB_STD = np.array([0.229, 0.224, 0.225], dtype="float32").reshape(3, 1, 1)


def read_manifest(manifest_path: Path) -> list[dict[str, str]]:
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def split_rows(rows: list[dict[str, str]], split: str) -> list[dict[str, str]]:
    return [row for row in rows if row["split"] == split]


def pil_to_rgb_tensor(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype="float32") / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    return (arr - RGB_MEAN) / RGB_STD


def compute_fft_tensor(image: Image.Image) -> np.ndarray:
    gray = np.asarray(image.convert("L"), dtype="float32") / 255.0
    spectrum = np.fft.fft2(gray)
    spectrum = np.fft.fftshift(spectrum)
    magnitude = np.log1p(np.abs(spectrum)).astype("float32")
    return normalize_frequency_map(magnitude)


def compute_highfreq_fft_tensor(image: Image.Image, low_radius_ratio: float = 0.18) -> np.ndarray:
    gray = np.asarray(image.convert("L"), dtype="float32") / 255.0
    spectrum = np.fft.fft2(gray)
    spectrum = np.fft.fftshift(spectrum)
    magnitude = np.log1p(np.abs(spectrum)).astype("float32")
    height, width = magnitude.shape
    yy, xx = np.ogrid[:height, :width]
    cy = (height - 1) / 2.0
    cx = (width - 1) / 2.0
    radius = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    max_radius = float(radius.max())
    cutoff = max_radius * low_radius_ratio
    highfreq = magnitude * (radius >= cutoff).astype("float32")
    return normalize_frequency_map(highfreq)


@lru_cache(maxsize=8)
def dct_matrix(size: int) -> np.ndarray:
    n = np.arange(size, dtype="float32")
    k = n.reshape(-1, 1)
    matrix = np.cos(np.pi * (2.0 * n + 1.0) * k / (2.0 * size)).astype("float32")
    matrix[0, :] *= np.sqrt(1.0 / size)
    matrix[1:, :] *= np.sqrt(2.0 / size)
    return matrix


def compute_dct_triband_tensor(
    image: Image.Image,
    low_cutoff: float = 0.25,
    mid_cutoff: float = 0.55,
) -> np.ndarray:
    gray = np.asarray(image.convert("L"), dtype="float32") / 255.0
    height, width = gray.shape
    dct_h = dct_matrix(height)
    dct_w = dct_matrix(width)
    coeff = dct_h @ gray @ dct_w.T
    magnitude = np.log1p(np.abs(coeff)).astype("float32")

    yy, xx = np.ogrid[:height, :width]
    y = yy.astype("float32") / max(height - 1, 1)
    x = xx.astype("float32") / max(width - 1, 1)
    radius = np.sqrt(x**2 + y**2) / np.sqrt(2.0)

    masks = [
        radius < low_cutoff,
        (radius >= low_cutoff) & (radius < mid_cutoff),
        radius >= mid_cutoff,
    ]
    bands = []
    for mask in masks:
        bands.append(normalize_single_map(magnitude * mask.astype("float32")))
    return np.stack(bands, axis=0).astype("float32")


def normalize_single_map(magnitude: np.ndarray) -> np.ndarray:
    min_value = float(magnitude.min())
    max_value = float(magnitude.max())
    if max_value > min_value:
        return ((magnitude - min_value) / (max_value - min_value)).astype("float32")
    return np.zeros_like(magnitude, dtype="float32")


def normalize_frequency_map(magnitude: np.ndarray) -> np.ndarray:
    return normalize_single_map(magnitude)[np.newaxis, :, :].astype("float32")


def compute_frequency_tensor(image: Image.Image, mode: str) -> np.ndarray:
    if mode == "fusion_fft":
        return compute_fft_tensor(image)
    if mode == "fusion_v2":
        return compute_highfreq_fft_tensor(image)
    if mode == "fusion_v3":
        return compute_dct_triband_tensor(image)
    raise ValueError(f"Unsupported frequency mode: {mode}")


def random_color_jitter(image: Image.Image) -> Image.Image:
    if random.random() < 0.5:
        image = ImageEnhance.Brightness(image).enhance(random.uniform(0.9, 1.1))
    if random.random() < 0.5:
        image = ImageEnhance.Contrast(image).enhance(random.uniform(0.9, 1.1))
    if random.random() < 0.3:
        image = ImageEnhance.Color(image).enhance(random.uniform(0.9, 1.1))
    return image


class FaceForgeryDataset(paddle.io.Dataset):
    def __init__(
        self,
        rows: list[dict[str, str]],
        data_root: Path,
        image_size: int = 224,
        mode: str = "rgb",
        augment: bool = False,
    ) -> None:
        super().__init__()
        if mode not in {"rgb", "fusion_fft", "fusion_v2", "fusion_v3"}:
            raise ValueError(f"Unsupported dataset mode: {mode}")
        self.rows = rows
        self.data_root = Path(data_root)
        self.image_size = image_size
        self.mode = mode
        self.augment = augment

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int):
        row = self.rows[index]
        image_path = self.data_root / row["face_image_path"]
        image = Image.open(image_path).convert("RGB")
        if image.size != (self.image_size, self.image_size):
            image = image.resize((self.image_size, self.image_size), Image.BILINEAR)

        if self.augment:
            if random.random() < 0.5:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image = random_color_jitter(image)

        rgb = pil_to_rgb_tensor(image).astype("float32")
        label = np.array(int(row["label"]), dtype="int64")
        if self.mode in {"fusion_fft", "fusion_v2", "fusion_v3"}:
            frequency = compute_frequency_tensor(image, self.mode)
            return rgb, frequency, label
        return rgb, label
