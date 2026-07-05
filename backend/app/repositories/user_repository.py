from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(select(User).where(User.username == username))

    def create_demo_user(self, username: str, password_hash: str, display_name: str) -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            display_name=display_name,
            status="active",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def touch_login(self, user: User) -> None:
        user.last_login_at = datetime.now()
        self.db.commit()

