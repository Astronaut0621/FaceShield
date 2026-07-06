from sqlalchemy.orm import Session

from app.algorithm.status import get_algorithm_status
from app.repositories.model_repository import ModelRepository
from app.serializers.model_serializer import serialize_model_version


class ModelService:
    def __init__(self, db: Session):
        self.repository = ModelRepository(db)

    def get_active_version(self) -> dict | None:
        model = self.repository.get_active()
        if model is None:
            return None
        data = serialize_model_version(model)
        data["algorithm"] = get_algorithm_status()
        return data
