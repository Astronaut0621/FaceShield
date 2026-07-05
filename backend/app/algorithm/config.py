import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AlgorithmSettings:
    backend: str = os.getenv("FACESHIELD_ALGORITHM_BACKEND", "mock")
    model_name: str = os.getenv("FACESHIELD_MODEL_NAME", "FaceShield-MockNet")
    model_version: str = os.getenv("FACESHIELD_MODEL_VERSION", "v0.1")
    model_path: str | None = os.getenv("FACESHIELD_MODEL_PATH")


algorithm_settings = AlgorithmSettings()

