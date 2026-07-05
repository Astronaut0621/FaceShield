from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    code: int = 200
    message: str = "success"
    data: DataT | None = None
