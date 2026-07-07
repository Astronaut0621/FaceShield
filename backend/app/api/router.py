from fastapi import APIRouter

from app.api import auth, asset, detect, detection, health, history, model, records, upload

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(asset.router)
api_router.include_router(detect.router)
api_router.include_router(upload.router)
api_router.include_router(detection.router)
api_router.include_router(history.router)
api_router.include_router(records.router)
api_router.include_router(model.router)
