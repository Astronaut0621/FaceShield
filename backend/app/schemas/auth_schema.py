from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserProfile(BaseModel):
    id: int
    username: str
    display_name: str | None
    status: str

