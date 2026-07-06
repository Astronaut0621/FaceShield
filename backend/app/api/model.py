from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_model_service
from app.domain.exceptions import NotFoundError
from app.models.user import User
from app.services.model_service import ModelService
from app.utils.response import success

router = APIRouter(prefix="/model-version", tags=["model"])


@router.get("")
def get_model_version(
    current_user: User = Depends(get_current_user),
    service: ModelService = Depends(get_model_service),
):
    data = service.get_active_version()
    if data is None:
        raise NotFoundError("Active model version not found.")
    return success(data, message="Query successful.")


@router.get("/list")
def list_model_versions(
    current_user: User = Depends(get_current_user),
    service: ModelService = Depends(get_model_service),
):
    return success(service.list_models(), message="Query successful.")

