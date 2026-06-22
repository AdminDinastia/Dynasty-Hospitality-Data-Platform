import enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Enum
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func

from app.core.database import Base


class PointsReason(enum.Enum):
    purchase = "purchase"  # bought with money
    welcome_bonus = "welcome_bonus"  # gift on registration
    data_used = "data_used"  # provider: their data used in aggregation
    product_access = "product_access"  # consumer: spent on product
    refund = "refund"  # refund
    manual = "manual"  # manual adjustment by admin


class PointsLedger(Base):
    __tablename__ = "points_ledger"

    ledger_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )

    # Positive (earned) or negative (spent)
    points: Mapped[int] = mapped_column(nullable=False)

    reason: Mapped[PointsReason] = mapped_column(Enum(PointsReason), nullable=False)

    # Reference to what caused this entry (payment_id, product_id, etc.)
    reference_id: Mapped[int | None] = mapped_column(nullable=True)
    reference_type: Mapped[str | None] = mapped_column(
        nullable=True
    )  # "payment", "product", "aggregation"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
