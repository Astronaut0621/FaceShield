from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion


class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active(self) -> ModelVersion | None:
        return self.db.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))

    def get_by_id(self, model_id: int) -> ModelVersion | None:
        return self.db.get(ModelVersion, model_id)

    def list_all(self) -> list[ModelVersion]:
        return list(
            self.db.scalars(
                select(ModelVersion).order_by(ModelVersion.is_active.desc(), ModelVersion.id.asc())
            )
        )

