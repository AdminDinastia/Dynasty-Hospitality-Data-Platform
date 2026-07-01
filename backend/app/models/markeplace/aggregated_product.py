import enum
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    DateTime,
    Enum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class AggregatedProductStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class AggregatedProduct(Base):
    __tablename__ = "aggregated_products"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)

    aggregation_id: Mapped[int] = mapped_column(
        ForeignKey("aggregations.aggregation_id"), nullable=False
    )
    template_name: Mapped[str] = mapped_column(nullable=False)  # "market_report"

    price_points: Mapped[int] = mapped_column(nullable=False)
    is_public: Mapped[bool] = mapped_column(default=True)
    is_featured: Mapped[bool] = mapped_column(default=False)
    status: Mapped[AggregatedProductStatus] = mapped_column(
        Enum(AggregatedProductStatus),
        nullable=False,
        default=AggregatedProductStatus.active,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
