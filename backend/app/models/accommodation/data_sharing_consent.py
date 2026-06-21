from app.core.database import Base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Boolean,
    String,
    DateTime,
    Numeric,
    func,
)


class DataSharingConsent(Base):
    __tablename__ = "data_sharing_consents"

    consent_id = Column(Integer, primary_key=True)
    accommodation_id = Column(
        Integer, ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )

    # What can be shared?
    allow_raw_sharing = Column(Boolean, nullable=False, default=False)
    allow_aggregated = Column(Boolean, nullable=False, default=False)

    # Monetization
    revenue_share_pct = Column(Numeric(5, 2), nullable=False, default=30.00)
    # Percentage received when individual data is sold

    # Auditing
    terms_version = Column(String, nullable=False)
    consent_given_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
