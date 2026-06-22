from decimal import Decimal
from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    DateTime,
    Numeric,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DataSharingConsent(Base):
    __tablename__ = "data_sharing_consents"

    consent_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )

    # What can be shared?
    allow_raw_sharing: Mapped[bool] = mapped_column(nullable=False, default=False)
    allow_aggregated: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Monetization
    revenue_share_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=30.00
    )
    # Percentage received when individual data is sold

    # Auditing
    terms_version: Mapped[str] = mapped_column(nullable=False)

    consent_given_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
