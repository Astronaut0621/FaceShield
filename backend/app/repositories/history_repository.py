from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.detection_result import DetectionResult
from app.models.detection_task import DetectionTask
from app.models.file_record import FileRecord


class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _filters(
        user_id: int | None = None,
        label: str | None = None,
        risk_level: str | None = None,
    ):
        filters = [FileRecord.is_deleted.is_(False)]
        if user_id is not None:
            filters.append(DetectionResult.user_id == user_id)
        if label:
            filters.append(DetectionResult.label == label)
        if risk_level:
            filters.append(DetectionResult.risk_level == risk_level)
        return filters

    def count(
        self,
        user_id: int | None = None,
        label: str | None = None,
        risk_level: str | None = None,
    ) -> int:
        stmt = (
            select(FileRecord)
            .select_from(DetectionResult)
            .join(DetectionTask, DetectionTask.id == DetectionResult.task_id)
            .join(FileRecord, FileRecord.id == DetectionResult.file_id)
            .where(*self._filters(user_id=user_id, label=label, risk_level=risk_level))
        )
        return len(self._filter_existing_file_records(list(self.db.scalars(stmt))))

    def list(
        self,
        *,
        offset: int,
        limit: int,
        user_id: int | None = None,
        label: str | None = None,
        risk_level: str | None = None,
    ):
        stmt = (
            select(DetectionResult, FileRecord)
            .join(DetectionTask, DetectionTask.id == DetectionResult.task_id)
            .join(FileRecord, FileRecord.id == DetectionResult.file_id)
            .where(*self._filters(user_id=user_id, label=label, risk_level=risk_level))
            .order_by(DetectionResult.created_at.desc(), DetectionResult.id.desc())
        )
        rows = self._filter_existing_rows(self.db.execute(stmt).all())
        return rows[offset : offset + limit]

    def get_detail(self, task_id: int, user_id: int | None = None):
        filters = [DetectionResult.task_id == task_id, FileRecord.is_deleted.is_(False)]
        if user_id is not None:
            filters.append(DetectionResult.user_id == user_id)
        stmt = (
            select(DetectionResult, FileRecord)
            .join(FileRecord, FileRecord.id == DetectionResult.file_id)
            .where(*filters)
        )
        row = self.db.execute(stmt).first()
        if row is None:
            return None
        return row if self._file_exists(row[1]) else self._mark_missing_and_return_none(row[1])

    def _filter_existing_rows(self, rows):
        active_rows = []
        missing_records = []
        for result, file_record in rows:
            if self._file_exists(file_record):
                active_rows.append((result, file_record))
            else:
                file_record.is_deleted = True
                missing_records.append(file_record)

        if missing_records:
            self.db.commit()

        return active_rows

    def _filter_existing_file_records(self, rows: list[FileRecord]) -> list[FileRecord]:
        active_rows = []
        missing_records = []
        for file_record in rows:
            if self._file_exists(file_record):
                active_rows.append(file_record)
            else:
                file_record.is_deleted = True
                missing_records.append(file_record)

        if missing_records:
            self.db.commit()

        return active_rows

    @staticmethod
    def _file_exists(file_record: FileRecord) -> bool:
        return bool(file_record.file_path) and Path(file_record.file_path).is_file()

    def _mark_missing_and_return_none(self, file_record: FileRecord):
        file_record.is_deleted = True
        self.db.commit()
        return None
