from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, DateTime, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.data.accommodation_data import GranularityType
from app.models.markeplace.product_status import ProductStatus


class RawProduct(Base):
    __tablename__ = "raw_products"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(nullable=False)
    granularity: Mapped[GranularityType] = mapped_column(
        Enum(GranularityType), nullable=False
    )

    # Specific hotel this product refers to
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id"), nullable=False
    )
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus),
        nullable=False,
        default=ProductStatus.draft,
        server_default="draft",
    )

    # Reference to JSON template in repo
    template_name: Mapped[str] = mapped_column(nullable=False)  # "hotel_report"

    # Partial data shown to non-paying users
    preview_config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Price in points
    price_points: Mapped[int] = mapped_column(nullable=False)

    is_public: Mapped[bool] = mapped_column(default=True)
    is_featured: Mapped[bool] = mapped_column(default=False)

    is_active: Mapped[bool] = mapped_column(
        nullable=False, default=True, server_default="true"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
