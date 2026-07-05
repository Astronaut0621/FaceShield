from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import get_current_user, get_file_service
from app.models.user import User
from app.serializers.file_serializer import serialize_file_record
from app.services.file_service import FileService
from app.utils.response import success

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    record = await service.save_upload_file(file, user_id=current_user.id)
    return success(serialize_file_record(record), message="Upload successful.")
