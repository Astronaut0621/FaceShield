from fastapi import APIRouter

from app.algorithm.status import get_algorithm_status
from app.utils.response import success

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return success(
        {
            "status": "ok",
            "algorithm": get_algorithm_status(),
        },
        message="FaceShield backend is running.",
    )
