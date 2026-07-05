from sqlalchemy.orm import Session

from app.repositories.model_repository import ModelRepository
from app.serializers.model_serializer import serialize_model_version


class ModelService:
    def __init__(self, db: Session):
        self.repository = ModelRepository(db)

    def get_active_version(self) -> dict | None:
        model = self.repository.get_active()
        if model is None:
            return None
        return serialize_model_version(model)

