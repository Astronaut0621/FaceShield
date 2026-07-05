from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DetectionTask(Base):
    __tablename__ = "detection_task"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("file_record.id"), nullable=False)
    task_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    task_type: Mapped[str] = mapped_column(String(50), default="image", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)

    user = relationship("User", back_populates="tasks")
    file = relationship("FileRecord", back_populates="tasks")
    result = relationship("DetectionResult", back_populates="task", uselist=False)
