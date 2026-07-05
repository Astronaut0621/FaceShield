import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import AppError
from app.utils.response import fail

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(exc.message, code=exc.status_code),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(str(exc.detail), code=exc.status_code),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content=fail("Internal server error.", code=500))

