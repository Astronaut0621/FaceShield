from typing import Any


def api_response(code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {"code": code, "message": message, "data": data}


def success(data: Any = None, message: str = "success", code: int = 200) -> dict[str, Any]:
    return api_response(code=code, message=message, data=data)


def fail(message: str, code: int = 400, data: Any = None) -> dict[str, Any]:
    return api_response(code=code, message=message, data=data)
