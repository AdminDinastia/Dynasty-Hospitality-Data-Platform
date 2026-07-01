import enum

from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Enum
from sqlalchemy.sql import func

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EntitlementType(str, enum.Enum):
    points = "points"  # paid with points (aggregated)
    granted = "granted"  # manually granted by platform


class Entitlement(Base):
    __tablename__ = "entitlements"

    entitlement_id: Mapped[int] = mapped_column(primary_key=True)

    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )

    # One of the two depending on product type
    aggregated_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("aggregated_products.product_id"), nullable=True
    )

    raw_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("raw_products.product_id"), nullable=True
    )

    entitlement_type: Mapped[EntitlementType] = mapped_column(
        Enum(EntitlementType), nullable=False
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
