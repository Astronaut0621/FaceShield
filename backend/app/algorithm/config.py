import os
from dataclasses import dataclass
from pathlib import Path


_BACKEND_DIR = Path(__file__).resolve().parents[2]
_PROJECT_DIR = _BACKEND_DIR.parent
_DEFAULT_DEPLOY_DIR = _PROJECT_DIR / "model" / "deploy" / "fusion_v2"


@dataclass(frozen=True)
class AlgorithmSettings:
    backend: str = os.getenv("FACESHIELD_ALGORITHM_BACKEND", "mock")
    model_name: str = os.getenv("FACESHIELD_MODEL_NAME", "FaceShield-FusionV2")
    model_version: str = os.getenv("FACESHIELD_MODEL_VERSION", "fusion_v2-202607")
    model_path: str | None = os.getenv(
        "FACESHIELD_MODEL_PATH",
        str(_DEFAULT_DEPLOY_DIR / "best.pdparams"),
    )
    model_config_path: str | None = os.getenv(
        "FACESHIELD_MODEL_CONFIG_PATH",
        str(_DEFAULT_DEPLOY_DIR / "config.json"),
    )
    crop_dir_name: str = "crops"


algorithm_settings = AlgorithmSettings()
