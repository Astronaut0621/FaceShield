from pathlib import Path
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.domain.exceptions import ValidationError


def safe_suffix(filename: str) -> str:
    return Path(filename or "").suffix.lower()


def validate_image_bytes(content: bytes) -> None:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
            if image.format not in {"JPEG", "PNG"}:
                raise ValidationError("Unsupported image format.")
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("Uploaded file is not a valid image.") from exc
