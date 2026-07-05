from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import get_current_user, get_detection_service, get_detection_workflow_service
from app.models.user import User
from app.schemas.detection_schema import DetectionStartRequest
from app.serializers.detection_serializer import serialize_detection_result
from app.services.detection_service import DetectionService
from app.services.detection_workflow_service import DetectionWorkflowService
from app.serializers.file_serializer import serialize_file_record
from app.serializers.record_serializer import serialize_detection_record
from app.utils.response import success

router = APIRouter(prefix="/detection", tags=["detection"])


@router.post("/start")
def start_detection_by_file(
    payload: DetectionStartRequest,
    current_user: User = Depends(get_current_user),
    service: DetectionService = Depends(get_detection_service),
):
    result = service.start_detection(payload.file_id, user_id=current_user.id)
    return success(serialize_detection_result(result), message="Detection completed.")


@router.post("/upload-and-detect")
async def upload_and_detect(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    service: DetectionWorkflowService = Depends(get_detection_workflow_service),
):
    workflow_result = await service.upload_and_detect(file, user_id=current_user.id)
    data = serialize_detection_result(workflow_result.detection_result)
    data["file"] = serialize_file_record(workflow_result.file_record)
    return success(data, message="Detection completed.")


@router.post("", include_in_schema=False)
async def detect_alias(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    service: DetectionWorkflowService = Depends(get_detection_workflow_service),
):
    workflow_result = await service.upload_and_detect(file, user_id=current_user.id)
    return success(
        serialize_detection_record(workflow_result.detection_result, workflow_result.file_record),
        message="Detection completed.",
    )
