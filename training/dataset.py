from __future__ import annotations

import csv
import random
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


def normalize_frequency_map(magnitude: np.ndarray) -> np.ndarray:
    min_value = float(magnitude.min())
    max_value = float(magnitude.max())
    if max_value > min_value:
        magnitude = (magnitude - min_value) / (max_value - min_value)
    else:
        magnitude = np.zeros_like(magnitude, dtype="float32")
    return magnitude[np.newaxis, :, :].astype("float32")


def compute_frequency_tensor(image: Image.Image, mode: str) -> np.ndarray:
    if mode == "fusion_fft":
        return compute_fft_tensor(image)
    if mode == "fusion_v2":
        return compute_highfreq_fft_tensor(image)
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
        if mode not in {"rgb", "fusion_fft", "fusion_v2"}:
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
        if self.mode in {"fusion_fft", "fusion_v2"}:
            frequency = compute_frequency_tensor(image, self.mode)
            return rgb, frequency, label
        return rgb, label
