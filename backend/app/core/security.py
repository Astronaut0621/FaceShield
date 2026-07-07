import base64
import hashlib
import hmac
import secrets
import time

from app.core.config import settings


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    actual = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(actual, expected)


def create_access_token(user_id: int, username: str) -> str:
    issued_at = str(int(time.time()))
    payload = f"{user_id}:{username}:{issued_at}"
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    raw_token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(raw_token.encode("utf-8")).decode("ascii")


def decode_access_token(token: str) -> tuple[int, str] | None:
    try:
        raw_token = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        user_id_text, username, issued_at, signature = raw_token.rsplit(":", 3)
        issued_at_seconds = int(issued_at)
    except Exception:
        return None

    payload = f"{user_id_text}:{username}:{issued_at}"
    expected = hmac.new(settings.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    if settings.ACCESS_TOKEN_EXPIRE_SECONDS > 0:
        if int(time.time()) - issued_at_seconds > settings.ACCESS_TOKEN_EXPIRE_SECONDS:
            return None
    return int(user_id_text), username
