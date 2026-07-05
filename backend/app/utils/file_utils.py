from pathlib import Path


def safe_suffix(filename: str) -> str:
    return Path(filename or "").suffix.lower()

