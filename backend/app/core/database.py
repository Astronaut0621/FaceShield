from collections.abc import Generator

from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.core.config import settings
    from app.core.security import hash_password
    from app.models import DetectionResult, DetectionTask, FileRecord, ModelVersion, User

    _ = (DetectionResult, DetectionTask, FileRecord, User)
    Base.metadata.create_all(bind=engine)
    _ensure_development_columns()

    with SessionLocal() as db:
        demo_user = db.scalar(select(User).where(User.username == settings.DEMO_USERNAME))
        if demo_user is None:
            db.add(
                User(
                    username=settings.DEMO_USERNAME,
                    password_hash=hash_password(settings.DEMO_PASSWORD),
                    display_name=settings.DEMO_DISPLAY_NAME,
                    status="active",
                )
            )
            db.commit()

        active_model = db.scalar(
            select(ModelVersion).where(
                ModelVersion.model_name == "FaceShield-MockNet",
                ModelVersion.version == "v0.1",
            )
        )
        if active_model is None:
            db.add(
                ModelVersion(
                    model_name="FaceShield-MockNet",
                    version="v0.1",
                    description="Initial mock detection model for frontend/backend integration.",
                    model_path=None,
                    is_active=True,
                )
            )
            db.commit()


def _ensure_development_columns() -> None:
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    expected_columns = {
        "file_record": {
            "user_id": "INTEGER",
            "image_hash": "VARCHAR(128)",
        },
        "detection_task": {
            "user_id": "INTEGER",
        },
        "detection_result": {
            "user_id": "INTEGER",
            "face_crop_url": "VARCHAR(500)",
            "face_detected": "BOOLEAN DEFAULT 0 NOT NULL",
        },
    }

    inspector = inspect(engine)
    with engine.begin() as connection:
        for table_name, columns in expected_columns.items():
            if not inspector.has_table(table_name):
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            for column_name, column_type in columns.items():
                if column_name not in existing:
                    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
