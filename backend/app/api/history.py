from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_current_user, get_history_service
from app.domain.exceptions import NotFoundError
from app.models.user import User
from app.services.history_service import HistoryService
from app.utils.response import success

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/list")
def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    label: str | None = Query(None),
    risk_level: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service),
):
    data = service.list_history(
        page=page,
        page_size=page_size,
        user_id=current_user.id,
        label=label,
        risk_level=risk_level,
    )
    return success(data, message="Query successful.")


@router.get("/{task_id}")
def get_history(
    task_id: int,
    current_user: User = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service),
):
    data = service.get_history_detail(task_id, user_id=current_user.id)
    if data is None:
        raise NotFoundError("Detection record not found.")
    return success(data, message="Query successful.")
