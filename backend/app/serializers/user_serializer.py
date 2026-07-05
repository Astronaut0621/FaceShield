from app.models.user import User
from app.utils.time_utils import format_datetime


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "status": user.status,
        "last_login_at": format_datetime(user.last_login_at),
    }

