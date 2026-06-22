import enum
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AggregationStatus(enum.Enum):
    pending = "pending"
    computing = "computing"
    ready = "ready"
    failed = "failed"


class Aggregation(Base):
    __tablename__ = "aggregations"

    aggregation_id: Mapped[int] = mapped_column(primary_key=True)
    aggregation_type: Mapped[str] = mapped_column(
        nullable=False
    )  # 'location', 'category'...
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    # {"level": "city", "location": "Gran Canaria"}

    storage_path: Mapped[str | None] = mapped_column(nullable=True)
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
