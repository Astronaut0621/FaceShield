from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.exception_handlers import (
    app_error_handler,
    generic_exception_handler,
    http_exception_handler,
)
from app.core.logger import configure_logging
from app.domain.exceptions import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_directories()
    init_db()
    yield


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="FaceShield Backend",
        description="Backend API for AI face forgery detection prototype.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")
    app.include_router(api_router, prefix=settings.API_PREFIX)

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    return app

