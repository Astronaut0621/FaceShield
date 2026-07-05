from sqlalchemy import func, select
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
            select(func.count())
            .select_from(DetectionResult)
            .join(DetectionTask, DetectionTask.id == DetectionResult.task_id)
            .join(FileRecord, FileRecord.id == DetectionResult.file_id)
            .where(*self._filters(user_id=user_id, label=label, risk_level=risk_level))
        )
        return self.db.scalar(stmt) or 0

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
            .offset(offset)
            .limit(limit)
        )
        return self.db.execute(stmt).all()

    def get_detail(self, task_id: int, user_id: int | None = None):
        filters = [DetectionResult.task_id == task_id, FileRecord.is_deleted.is_(False)]
        if user_id is not None:
            filters.append(DetectionResult.user_id == user_id)
        stmt = (
            select(DetectionResult, FileRecord)
            .join(FileRecord, FileRecord.id == DetectionResult.file_id)
            .where(*filters)
        )
        return self.db.execute(stmt).first()
