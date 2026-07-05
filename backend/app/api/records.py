from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_history_service
from app.domain.exceptions import NotFoundError
from app.models.user import User
from app.services.history_service import HistoryService
from app.utils.response import success

router = APIRouter(prefix="/records", tags=["records"])


@router.get("")
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service),
):
    return success(
        service.list_history(page=page, page_size=page_size, user_id=current_user.id),
        message="Query successful.",
    )


@router.get("/{record_id}")
def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service),
):
    data = service.get_history_detail(record_id, user_id=current_user.id)
    if data is None:
        raise NotFoundError("Detection record not found.")
    return success(data, message="Query successful.")

