import enum
from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Integer, Enum, String, DateTime, func


class UploadStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Upload(Base):
    __tablename__ = "uploads"

    upload_id = Column(Integer, primary_key=True)
    org_id = Column(ForeignKey("organizations.org_id"), nullable=False)

    status = Column(
        Enum(UploadStatus, name="upload_status"),
        nullable=False,
        default=UploadStatus.pending,
    )

    error_message = Column(String, nullable=True)

    file_path = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
