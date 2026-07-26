import enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, String, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    payment_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )

    # Amount in cents
    amount: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="EUR"
    )  # ISO 4217

    # Points awarded for this payment
    points_awarded: Mapped[int] = mapped_column(nullable=False)

    # Stripe payment reference
    stripe_payment_id: Mapped[str | None] = mapped_column(nullable=True)

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
