from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MarketReport(Base):
    __tablename__ = "market_reports"

    report_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    aggregated_product_id: Mapped[int] = mapped_column(
        ForeignKey("aggregated_products.product_id"), nullable=False
    )

    # Saved filters for easy repeat queries
    filters: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AccommodationReport(Base):
    __tablename__ = "accommodation_reports"

    report_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    raw_product_id: Mapped[int] = mapped_column(
        ForeignKey("raw_products.product_id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
