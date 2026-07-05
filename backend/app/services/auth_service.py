from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.domain.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.serializers.user_serializer import serialize_user


class AuthService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def login(self, username: str, password: str) -> dict:
        user = self.repository.get_by_username(username)
        if user is None or user.status != "active" or not verify_password(password, user.password_hash):
            raise ValidationError("Invalid username or password.")

        self.repository.touch_login(user)
        return {
            "access_token": create_access_token(user.id, user.username),
            "token_type": "bearer",
            "user": serialize_user(user),
        }

    def get_current_profile(self, user: User) -> dict:
        return serialize_user(user)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if user is None or user.status != "active":
            raise NotFoundError("User not found.")
        return user

