from fastapi import APIRouter, Depends

from app.api.dependencies import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth_schema import LoginRequest
from app.services.auth_service import AuthService
from app.utils.response import success

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return success(service.login(payload.username, payload.password), message="Login successful.")


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return success({"status": "ok"}, message="Logout successful.")


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return success(service.get_current_profile(current_user), message="Query successful.")

