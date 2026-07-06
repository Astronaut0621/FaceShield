from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class FaceCropResult:
    crop_path: str
    crop_url: str
    face_detected: bool
    bbox: tuple[int, int, int, int] | None = None


def preprocess_image(image_path: str) -> str:
    return image_path


def crop_face_for_detection(
    image_path: str,
    output_dir: str | Path,
    output_url_prefix: str = "/storage/crops",
    image_size: int = 224,
    expand_ratio: float = 1.3,
) -> FaceCropResult:
    source_path = Path(image_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    image = Image.open(source_path).convert("RGB")
    bbox = _detect_largest_face(image)
    face_detected = bbox is not None
    if bbox is None:
        bbox = _center_square_bbox(image.width, image.height)
    else:
        bbox = _expand_to_square_bbox(bbox, image.width, image.height, expand_ratio)

    crop = image.crop(bbox).resize((image_size, image_size), Image.BILINEAR)
    crop_filename = f"{source_path.stem}_{uuid4().hex[:12]}.jpg"
    crop_file = output_path / crop_filename
    crop.save(crop_file, format="JPEG", quality=92)

    return FaceCropResult(
        crop_path=str(crop_file),
        crop_url=f"{output_url_prefix}/{crop_filename}",
        face_detected=face_detected,
        bbox=bbox,
    )


def _detect_largest_face(image: Image.Image) -> tuple[int, int, int, int] | None:
    try:
        import cv2
    except ImportError:
        return None
    if not hasattr(cv2, "CascadeClassifier") or not hasattr(cv2, "data"):
        return None

    gray = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2GRAY)
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        return None

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(40, 40),
    )
    if len(faces) == 0:
        return None

    x, y, width, height = max(faces, key=lambda face: int(face[2]) * int(face[3]))
    return int(x), int(y), int(x + width), int(y + height)


def _center_square_bbox(width: int, height: int) -> tuple[int, int, int, int]:
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    return left, top, left + side, top + side


def _expand_to_square_bbox(
    bbox: tuple[int, int, int, int],
    image_width: int,
    image_height: int,
    expand_ratio: float,
) -> tuple[int, int, int, int]:
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top
    side = max(width, height) * expand_ratio
    center_x = (left + right) / 2.0
    center_y = (top + bottom) / 2.0

    new_left = int(round(center_x - side / 2.0))
    new_top = int(round(center_y - side / 2.0))
    new_right = int(round(center_x + side / 2.0))
    new_bottom = int(round(center_y + side / 2.0))

    if new_left < 0:
        new_right -= new_left
        new_left = 0
    if new_top < 0:
        new_bottom -= new_top
        new_top = 0
    if new_right > image_width:
        shift = new_right - image_width
        new_left = max(0, new_left - shift)
        new_right = image_width
    if new_bottom > image_height:
        shift = new_bottom - image_height
        new_top = max(0, new_top - shift)
        new_bottom = image_height

    side = min(new_right - new_left, new_bottom - new_top)
    return new_left, new_top, new_left + side, new_top + side
