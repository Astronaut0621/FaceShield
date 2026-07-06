import os
from pathlib import Path


class Settings:
    APP_NAME = "FaceShield"
    API_PREFIX = "/api"
    BASE_DIR = Path(__file__).resolve().parents[2]
    STORAGE_DIR = BASE_DIR / "storage"
    UPLOAD_DIR = STORAGE_DIR / "uploads"
    REPORT_DIR = STORAGE_DIR / "reports"
    HEATMAP_DIR = STORAGE_DIR / "heatmaps"
    CROP_DIR = STORAGE_DIR / "crops"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'faceshield.db'}",
    )

    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
    SECRET_KEY = os.getenv("SECRET_KEY", "faceshield-dev-secret-change-me")
    DEMO_USERNAME = os.getenv("DEMO_USERNAME", "demo")
    DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo123456")
    DEMO_DISPLAY_NAME = os.getenv("DEMO_DISPLAY_NAME", "Demo User")
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]

    def ensure_directories(self) -> None:
        for directory in [
            self.STORAGE_DIR,
            self.UPLOAD_DIR,
            self.REPORT_DIR,
            self.HEATMAP_DIR,
            self.CROP_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
