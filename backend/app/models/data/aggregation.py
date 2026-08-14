import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.accommodation.accommodation import CategorySystem, AccommodationType


class AggregationStatus(str, enum.Enum):
    pending = "pending"
    computing = "computing"
    ready = "ready"
    failed = "failed"


class AggregationParameters(BaseModel):
    # Geographic
    nuts1: str | None = None
    nuts2: str | None = None
    nuts3: str | None = None
    country: str | None = None
    city: str | None = None
    # Chain
    org_id: int | None = None
    # Common filters
    category_system: CategorySystem | None = None
    min_category: float | None = None
    max_category: float | None = None
    type: AccommodationType | None = None
    year_from: int | None = None
    year_to: int | None = None


class Aggregation(Base):
    __tablename__ = "aggregations"

    aggregation_id: Mapped[int] = mapped_column(primary_key=True)
    aggregation_type: Mapped[str] = mapped_column(
        nullable=False
    )  # 'location', 'category'...
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    # {"level": "city", "location": "Gran Canaria"}

    storage_path: Mapped[str | None] = mapped_column(nullable=True)
    is_precomputed: Mapped[bool] = mapped_column(default=True, server_default="true")
    status: Mapped[AggregationStatus] = mapped_column(
        Enum(AggregationStatus), nullable=False, default=AggregationStatus.pending
    )

    computed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
