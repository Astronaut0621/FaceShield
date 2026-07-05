from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileRecord(Base):
    __tablename__ = "file_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    image_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(500))
    file_type: Mapped[str | None] = mapped_column(String(50))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="files")
    tasks = relationship("DetectionTask", back_populates="file")
    results = relationship("DetectionResult", back_populates="file")
