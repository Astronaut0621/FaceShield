from datetime import datetime, timezone

from app.algorithm.status import get_algorithm_status
from app.core.config import settings
from app.schemas.mobile_schema import (
    MobileAlgorithmInfo,
    MobileBootstrapResponse,
    MobileEndpointInfo,
    MobileUploadPolicy,
)


class MobileConnectivityService:
    """Builds the stable startup payload consumed by Android clients."""

    def get_bootstrap(self) -> MobileBootstrapResponse:
        algorithm = get_algorithm_status()
        return MobileBootstrapResponse(
            status="ok",
            api_version="v1",
            server_time=datetime.now(timezone.utc).isoformat(),
            endpoints=MobileEndpointInfo(
                login=f"{settings.API_PREFIX}/auth/login",
                detect=f"{settings.API_PREFIX}/detect",
                records=f"{settings.API_PREFIX}/records",
                model_version=f"{settings.API_PREFIX}/model-version",
            ),
            upload_policy=MobileUploadPolicy(
                max_upload_size=settings.MAX_UPLOAD_SIZE,
                allowed_extensions=sorted(settings.ALLOWED_EXTENSIONS),
            ),
            algorithm=MobileAlgorithmInfo(
                backend=str(algorithm.get("backend", "")),
                ready=bool(algorithm.get("ready", False)),
                model_name=algorithm.get("model_name"),
                model_version=algorithm.get("model_version"),
                warnings=list(algorithm.get("warnings") or []),
            ),
        )
