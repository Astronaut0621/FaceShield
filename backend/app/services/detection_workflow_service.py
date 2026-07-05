from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.detection_result import DetectionResult
from app.models.file_record import FileRecord
from app.services.detection_service import DetectionService
from app.services.file_service import FileService


class DetectionWorkflowResult:
    def __init__(self, file_record: FileRecord, detection_result: DetectionResult):
        self.file_record = file_record
        self.detection_result = detection_result


class DetectionWorkflowService:
    def __init__(self, db: Session):
        self.file_service = FileService(db)
        self.detection_service = DetectionService(db)

    async def upload_and_detect(self, file: UploadFile, user_id: int | None = None) -> DetectionWorkflowResult:
        file_record = await self.file_service.save_upload_file(file, user_id=user_id)
        detection_result = self.detection_service.start_detection(file_record.id, user_id=user_id)
        return DetectionWorkflowResult(file_record=file_record, detection_result=detection_result)
