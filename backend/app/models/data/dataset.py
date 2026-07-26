import enum
from datetime import date, datetime

from sqlalchemy import ForeignKey, Date, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DatasetState(str, enum.Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"


class Dataset(Base):
    __tablename__ = "datasets"

    dataset_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id"), nullable=False
    )
    source_upload_id: Mapped[int | None] = mapped_column(
        ForeignKey("uploads.upload_id"), nullable=True
    )

    name: Mapped[str] = mapped_column(nullable=False)
    granularity: Mapped[str | None] = mapped_column(nullable=True)  # flexible

    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    storage_path: Mapped[str] = mapped_column(nullable=False)
    currency: Mapped[str | None] = mapped_column(nullable=True)  # optional

    is_active: Mapped[bool] = mapped_column(default=True)
    state: Mapped[DatasetState] = mapped_column(
        Enum(DatasetState), nullable=False, default=DatasetState.draft
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
