from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.domain.exceptions import AppError
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.database import get_db
from app.services.detection_service import DetectionService
from app.services.detection_workflow_service import DetectionWorkflowService
from app.services.file_service import FileService
from app.services.history_service import HistoryService
from app.services.model_service import ModelService

bearer_scheme = HTTPBearer(auto_error=False)


class UnauthorizedError(AppError):
    status_code = 401
    message = "Authentication required."


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError()
    decoded = decode_access_token(credentials.credentials)
    if decoded is None:
        raise UnauthorizedError("Invalid or expired token.")
    user_id, _username = decoded
    return service.get_user_by_id(user_id)


def get_file_service(db: Session = Depends(get_db)) -> FileService:
    return FileService(db)


def get_detection_service(db: Session = Depends(get_db)) -> DetectionService:
    return DetectionService(db)


def get_detection_workflow_service(db: Session = Depends(get_db)) -> DetectionWorkflowService:
    return DetectionWorkflowService(db)


def get_history_service(db: Session = Depends(get_db)) -> HistoryService:
    return HistoryService(db)


def get_model_service(db: Session = Depends(get_db)) -> ModelService:
    return ModelService(db)
