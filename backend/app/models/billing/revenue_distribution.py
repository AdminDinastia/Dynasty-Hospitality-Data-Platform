import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RevenueDistributionStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class RevenueDistribution(Base):
    __tablename__ = "revenue_distributions"

    distribution_id: Mapped[int] = mapped_column(primary_key=True)

    # What product was sold
    raw_product_id: Mapped[int] = mapped_column(
        ForeignKey("raw_products.product_id"), nullable=False
    )
    # Who bought it
    buyer_org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    # Which organization receives the payment (Stripe Connect level)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    # Which specific accommodation generated the revenue
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id"), nullable=False
    )

    # Amount in cents
    amount: Mapped[int] = mapped_column(nullable=False)

    # Revenue share % at the time of the transaction (historical record)
    revenue_share_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    # Stripe Connect payout reference
    stripe_transfer_id: Mapped[str | None] = mapped_column(nullable=True)

    status: Mapped[RevenueDistributionStatus] = mapped_column(
        Enum(RevenueDistributionStatus),
        nullable=False,
        default=RevenueDistributionStatus.pending,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
