from sqlalchemy.orm import Session

from app.models.file_record import FileRecord


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active(self, file_id: int, user_id: int | None = None) -> FileRecord | None:
        record = self.db.get(FileRecord, file_id)
        if record is None or record.is_deleted:
            return None
        if user_id is not None and record.user_id != user_id:
            return None
        return record

    def create(
        self,
        *,
        original_filename: str,
        stored_filename: str,
        image_hash: str,
        file_path: str,
        file_url: str,
        file_type: str,
        file_size: int,
        user_id: int | None = None,
    ) -> FileRecord:
        record = FileRecord(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            image_hash=image_hash,
            file_path=file_path,
            file_url=file_url,
            file_type=file_type,
            file_size=file_size,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
