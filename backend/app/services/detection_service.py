from decimal import Decimal

from sqlalchemy.orm import Session

from app.algorithm.predictor import predict_image
from app.domain.exceptions import DetectionFailedError, NotFoundError
from app.domain.risk_policy import RiskPolicy
from app.models.detection_result import DetectionResult
from app.repositories.detection_repository import DetectionRepository
from app.repositories.file_repository import FileRepository


class DetectionService:
    def __init__(self, db: Session):
        self.file_repository = FileRepository(db)
        self.detection_repository = DetectionRepository(db)

    def start_detection(self, file_id: int, user_id: int | None = None) -> DetectionResult:
        file_record = self.file_repository.get_active(file_id, user_id=user_id)
        if file_record is None:
            raise NotFoundError("File record not found.")

        task = self.detection_repository.create_task(file_id=file_id, user_id=user_id)

        try:
            self.detection_repository.mark_task_running(task)

            prediction = predict_image(file_record.file_path)
            fake_probability = float(prediction["fake_probability"])
            risk_level = RiskPolicy.classify(fake_probability)
            heatmap_url = prediction.get("heatmap_url") or prediction.get("heatmap_path")

            result = self.detection_repository.create_result(
                task_id=task.id,
                user_id=user_id,
                file_id=file_id,
                label=prediction.get("label"),
                fake_probability=Decimal(str(fake_probability)),
                confidence=Decimal(str(prediction.get("confidence", 0))),
                risk_level=risk_level.value,
                frequency_score=Decimal(str(prediction.get("frequency_score", 0))),
                spatial_score=Decimal(str(prediction.get("spatial_score", 0))),
                heatmap_url=heatmap_url,
                face_crop_url=None,
                face_detected=False,
                suggestion=RiskPolicy.suggestion_for(risk_level),
                model_name=prediction.get("model_name"),
                model_version=prediction.get("model_version"),
            )

            self.detection_repository.mark_task_success(task)
            return result
        except Exception as exc:
            self.detection_repository.mark_task_failed(task, str(exc))
            raise DetectionFailedError() from exc


def start_detection(db: Session, file_id: int) -> DetectionResult:
    return DetectionService(db).start_detection(file_id)
