import enum
from sqlalchemy import Column, Integer, String, DateTime, func, Enum
from app.core.database import Base


class OrganizationType(enum.Enum):
    provider = "provider"
    consumer = "consumer"


class Organization(Base):
    __tablename__ = "organizations"

    org_id = Column(Integer, primary_key=True)
    name = Column(String)
    # Type of organization in the marketplace
    type = Column(Enum(OrganizationType), nullable=False)

    # Monetization
    points_balance = Column(Integer, nullable=False, default=0)

    # Providers (receive money)
    stripe_account_id = Column(String, nullable=True)

    # Conumers (pay money)
    stripe_customer_id = Column(String, nullable=True)

    # Timestamps managed automatically by the database
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
