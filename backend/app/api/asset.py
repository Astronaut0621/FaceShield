from fastapi import APIRouter, Depends, UploadFile, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_file_service, get_db
from app.models.user import User
from app.serializers.file_serializer import serialize_file_record
from app.services.asset_service import AssetService
from app.services.file_service import FileService
from app.utils.response import success

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/upload")
async def upload_asset(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    service: FileService = Depends(get_file_service),
):
    record = await service.save_upload_file(file, user_id=current_user.id)
    return success(serialize_file_record(record), message="Upload successful.")


@router.get("/list")
def list_assets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AssetService(db)
    return success(service.list_assets(user_id=current_user.id, page=page, page_size=page_size), message="Query successful.")


@router.get("/{file_id}")
def get_asset(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AssetService(db)
    asset = service.get_asset(file_id=file_id, user_id=current_user.id)
    if asset is None:
        return success(None, message="Asset not found.")
    return success(serialize_file_record(asset), message="Query successful.")
