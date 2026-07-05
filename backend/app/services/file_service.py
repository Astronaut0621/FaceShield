from datetime import datetime
import hashlib
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.file_policy import UploadFilePolicy
from app.models.file_record import FileRecord
from app.repositories.file_repository import FileRepository


class FileService:
    def __init__(self, db: Session):
        self.repository = FileRepository(db)

    async def save_upload_file(self, file: UploadFile, user_id: int | None = None) -> FileRecord:
        suffix = UploadFilePolicy.validate_filename(file.filename)
        content = await file.read()
        UploadFilePolicy.validate_content(content)
        image_hash = hashlib.sha256(content).hexdigest()

        settings.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stored_filename = f"{timestamp}_{uuid4()}{suffix}"
        file_path = settings.UPLOAD_DIR / stored_filename
        file_path.write_bytes(content)

        return self.repository.create(
            original_filename=file.filename,
            stored_filename=stored_filename,
            image_hash=image_hash,
            file_path=str(file_path),
            file_url=f"/storage/uploads/{stored_filename}",
            file_type=suffix.lstrip("."),
            file_size=len(content),
            user_id=user_id,
        )


async def save_upload_file(db: Session, file: UploadFile) -> FileRecord:
    return await FileService(db).save_upload_file(file)
