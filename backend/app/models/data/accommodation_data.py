import enum
from datetime import date, datetime

from sqlalchemy import ForeignKey, Date, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GranularityType(str, enum.Enum):
    annual = "annual"
    quarterly = "quarterly"
    monthly = "monthly"


class AccommodationDataState(str, enum.Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"


class AccommodationData(Base):
    __tablename__ = "accommodation_data"

    accommodation_data_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id"), nullable=False
    )
    raw_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("raw_products.product_id", ondelete="SET NULL"), nullable=True
    )
    source_upload_id: Mapped[int | None] = mapped_column(
        ForeignKey("uploads.upload_id"), nullable=True
    )

    granularity: Mapped[GranularityType] = mapped_column(
        Enum(GranularityType),
        nullable=False,
        default=GranularityType.annual,
        server_default="annual",
    )  # flexible
    name: Mapped[str] = mapped_column(nullable=False)

    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    storage_path: Mapped[str] = mapped_column(nullable=False)
    currency: Mapped[str | None] = mapped_column(nullable=True)  # optional

    is_active: Mapped[bool] = mapped_column(default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    state: Mapped[AccommodationDataState] = mapped_column(
        Enum(AccommodationDataState),
        nullable=False,
        default=AccommodationDataState.draft,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
