import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum
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

    ledger_id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)

    # Positive (earned) or negative (spent)
    points = Column(Integer, nullable=False)

    reason = Column(Enum(PointsReason), nullable=False)

    # Reference to what caused this entry (payment_id, product_id, etc.)
    reference_id = Column(Integer, nullable=True)
    reference_type = Column(
        String, nullable=True
    )  # "payment", "product", "aggregation"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
