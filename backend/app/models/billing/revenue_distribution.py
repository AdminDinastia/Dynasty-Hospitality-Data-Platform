import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Numeric, String
from sqlalchemy.sql import func
from app.core.database import Base


class RevenueDistributionStatus(enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"


class RevenueDistribution(Base):
    __tablename__ = "revenue_distributions"

    distribution_id = Column(Integer, primary_key=True)

    # What product was sold
    raw_product_id = Column(
        Integer, ForeignKey("raw_products.product_id"), nullable=False
    )

    # Who bought it
    buyer_org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)

    # Which organization receives the payment (Stripe Connect level)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)

    # Which specific accommodation generated the revenue
    accommodation_id = Column(Integer, ForeignKey("accommodations.id"), nullable=False)

    # Amount in cents
    amount = Column(Integer, nullable=False)

    # Revenue share % at the time of the transaction (historical record)
    revenue_share_pct = Column(Numeric(5, 2), nullable=False)

    # Stripe Connect payout reference
    stripe_transfer_id = Column(String, nullable=True)

    status = Column(
        Enum(RevenueDistributionStatus),
        nullable=False,
        default=RevenueDistributionStatus.pending,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
