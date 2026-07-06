from app.core.config import settings
from app.domain.exceptions import ValidationError
from app.utils.file_utils import safe_suffix
from app.utils.file_utils import validate_image_bytes


class UploadFilePolicy:
    @staticmethod
    def validate_filename(filename: str | None) -> str:
        if not filename:
            raise ValidationError("No file selected.")

        suffix = safe_suffix(filename)
        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise ValidationError("Unsupported image format.")
        return suffix

    @staticmethod
    def validate_content(content: bytes) -> None:
        if not content:
            raise ValidationError("Uploaded file is empty.")
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise ValidationError("Image size exceeds 10MB.")
        validate_image_bytes(content)
