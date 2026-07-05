from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DetectionResult(Base):
    __tablename__ = "detection_result"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("detection_task.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("file_record.id"), nullable=False)
    label: Mapped[str | None] = mapped_column(String(50))
    fake_probability: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    risk_level: Mapped[str | None] = mapped_column(String(50))
    frequency_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    spatial_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    heatmap_url: Mapped[str | None] = mapped_column(String(500))
    face_crop_url: Mapped[str | None] = mapped_column(String(500))
    face_detected: Mapped[bool] = mapped_column(default=False, nullable=False)
    suggestion: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(String(100))
    model_version: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="results")
    task = relationship("DetectionTask", back_populates="result")
    file = relationship("FileRecord", back_populates="results")
