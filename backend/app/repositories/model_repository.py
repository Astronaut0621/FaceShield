from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion


class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active(self) -> ModelVersion | None:
        return self.db.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))

