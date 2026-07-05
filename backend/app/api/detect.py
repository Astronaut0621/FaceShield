from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import get_current_user, get_detection_workflow_service
from app.models.user import User
from app.serializers.record_serializer import serialize_detection_record
from app.services.detection_workflow_service import DetectionWorkflowService
from app.utils.response import success

router = APIRouter(tags=["detection"])


@router.post("/detect")
async def detect(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    service: DetectionWorkflowService = Depends(get_detection_workflow_service),
):
    workflow_result = await service.upload_and_detect(file, user_id=current_user.id)
    return success(
        serialize_detection_record(workflow_result.detection_result, workflow_result.file_record),
        message="Detection completed.",
    )

