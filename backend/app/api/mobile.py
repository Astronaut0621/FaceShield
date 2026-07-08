from fastapi import APIRouter, Depends

from app.api.dependencies import get_mobile_connectivity_service
from app.services.mobile_connectivity_service import MobileConnectivityService
from app.utils.response import success

router = APIRouter(prefix="/mobile", tags=["mobile"])


@router.get("/bootstrap")
def mobile_bootstrap(
    service: MobileConnectivityService = Depends(get_mobile_connectivity_service),
):
    payload = service.get_bootstrap()
    return success(
        payload.model_dump() if hasattr(payload, "model_dump") else payload.dict(),
        message="Mobile bootstrap loaded.",
    )
