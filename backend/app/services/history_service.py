from sqlalchemy.orm import Session

from app.repositories.history_repository import HistoryRepository
from app.serializers.history_serializer import serialize_history_detail, serialize_history_item


class HistoryService:
    def __init__(self, db: Session):
        self.repository = HistoryRepository(db)

    def list_history(
        self,
        page: int = 1,
        page_size: int = 10,
        user_id: int | None = None,
        label: str | None = None,
        risk_level: str | None = None,
    ) -> dict:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        total = self.repository.count(user_id=user_id, label=label, risk_level=risk_level)
        rows = self.repository.list(
            offset=(page - 1) * page_size,
            limit=page_size,
            user_id=user_id,
            label=label,
            risk_level=risk_level,
        )
        return {
            "total": total,
            "items": [serialize_history_item(result, file_record) for result, file_record in rows],
        }

    def get_history_detail(self, task_id: int, user_id: int | None = None) -> dict | None:
        row = self.repository.get_detail(task_id, user_id=user_id)
        if row is None:
            return None

        result, file_record = row
        return serialize_history_detail(result, file_record)


def list_history(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    user_id: int | None = None,
    label: str | None = None,
    risk_level: str | None = None,
) -> dict:
    return HistoryService(db).list_history(
        page=page,
        page_size=page_size,
        user_id=user_id,
        label=label,
        risk_level=risk_level,
    )


def get_history_detail(db: Session, task_id: int, user_id: int | None = None) -> dict | None:
    return HistoryService(db).get_history_detail(task_id, user_id=user_id)
