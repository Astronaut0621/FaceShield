from pathlib import Path

from sqlalchemy import func, select
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
        if not self._file_exists(record):
            self._mark_deleted(record)
            return None
        return record

    def list_by_user(
        self,
        user_id: int,
        offset: int = 0,
        limit: int = 20,
    ) -> list[FileRecord]:
        stmt = (
            select(FileRecord)
            .where(FileRecord.user_id == user_id, FileRecord.is_deleted.is_(False))
            .order_by(FileRecord.upload_time.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = list(self.db.scalars(stmt))
        return self._filter_existing(rows)

    def count_by_user(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(FileRecord)
            .where(FileRecord.user_id == user_id, FileRecord.is_deleted.is_(False))
        )
        return self.db.scalar(stmt) or 0

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

    def _filter_existing(self, rows: list[FileRecord]) -> list[FileRecord]:
        active_rows = []
        missing_rows = []
        for row in rows:
            if self._file_exists(row):
                active_rows.append(row)
            else:
                row.is_deleted = True
                missing_rows.append(row)

        if missing_rows:
            self.db.commit()

        return active_rows

    @staticmethod
    def _file_exists(record: FileRecord) -> bool:
        return bool(record.file_path) and Path(record.file_path).is_file()

    def _mark_deleted(self, record: FileRecord) -> None:
        record.is_deleted = True
        self.db.commit()
