import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Enum
from sqlalchemy.sql import func
from app.core.database import Base


class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    payment_id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)

    # Amount in cents
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")  # ISO 4217

    # Points awarded for this payment
    points_awarded = Column(Integer, nullable=False)

    # Stripe payment reference
    stripe_payment_id = Column(String, nullable=True)

    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
