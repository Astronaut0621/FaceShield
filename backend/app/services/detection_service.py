import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.algorithm.postprocess.heatmap import generate_fallback_heatmap
from app.algorithm.preprocess import crop_face_for_detection
from app.algorithm.predictor import predict_image
from app.core.config import settings
from app.domain.exceptions import DetectionFailedError, NotFoundError
from app.domain.risk_policy import RiskPolicy
from app.models.detection_result import DetectionResult
from app.repositories.detection_repository import DetectionRepository
from app.repositories.file_repository import FileRepository
from app.repositories.model_repository import ModelRepository

logger = logging.getLogger(__name__)


class DetectionService:
    def __init__(self, db: Session):
        self.file_repository = FileRepository(db)
        self.detection_repository = DetectionRepository(db)
        self.model_repository = ModelRepository(db)

    def start_detection(
        self,
        file_id: int,
        user_id: int | None = None,
        model_id: int | None = None,
    ) -> DetectionResult:
        file_record = self.file_repository.get_active(file_id, user_id=user_id)
        if file_record is None:
            raise NotFoundError("File record not found.")

        task = self.detection_repository.create_task(file_id=file_id, user_id=user_id)

        try:
            self.detection_repository.mark_task_running(task)
            logger.info(
                "Starting detection task_id=%s file_id=%s user_id=%s path=%s",
                task.id,
                file_id,
                user_id,
                file_record.file_path,
            )

            crop = crop_face_for_detection(
                file_record.file_path,
                output_dir=settings.CROP_DIR,
                output_url_prefix="/storage/crops",
            )
            logger.info(
                "Prepared face crop task_id=%s face_detected=%s crop_path=%s",
                task.id,
                crop.face_detected,
                crop.crop_path,
            )
            prediction = predict_image(crop.crop_path)
            fake_probability = float(prediction["fake_probability"])
            risk_level = RiskPolicy.classify(fake_probability)
            heatmap_url = prediction.get("heatmap_url") or prediction.get("heatmap_path")
            if not heatmap_url:
                heatmap = generate_fallback_heatmap(
                    crop.crop_path,
                    output_dir=settings.HEATMAP_DIR,
                    output_url_prefix="/storage/heatmaps",
                )
                heatmap_url = heatmap.heatmap_url

            selected_model = self.model_repository.get_by_id(model_id) if model_id else None
            model_name = prediction.get("model_name")
            model_version = prediction.get("model_version")
            if selected_model is not None:
                model_name = selected_model.model_name
                model_version = selected_model.version

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
                face_crop_url=crop.crop_url,
                face_detected=crop.face_detected,
                suggestion=RiskPolicy.suggestion_for(risk_level),
                model_name=model_name,
                model_version=model_version,
            )

            self.detection_repository.mark_task_success(task)
            logger.info(
                "Detection completed task_id=%s label=%s fake_probability=%.4f risk=%s model=%s/%s",
                task.id,
                result.label,
                fake_probability,
                risk_level.value,
                result.model_name,
                result.model_version,
            )
            return result
        except Exception as exc:
            self.detection_repository.mark_task_failed(task, str(exc))
            logger.exception("Detection failed task_id=%s file_id=%s user_id=%s", task.id, file_id, user_id)
            raise DetectionFailedError() from exc


def start_detection(db: Session, file_id: int) -> DetectionResult:
    return DetectionService(db).start_detection(file_id)
