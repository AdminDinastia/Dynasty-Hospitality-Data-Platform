import enum
from datetime import datetime

from sqlalchemy import DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OrganizationType(str, enum.Enum):
    provider = "provider"
    consumer = "consumer"


class Organization(Base):
    __tablename__ = "organizations"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    # Type of organization in the marketplace
    type: Mapped[OrganizationType] = mapped_column(
        Enum(OrganizationType), nullable=False
    )

    # Monetization
    points_balance: Mapped[int] = mapped_column(nullable=False, default=0)

    # Providers (receive money)
    stripe_account_id: Mapped[str | None] = mapped_column(nullable=True)
    # Consumers (pay money)
    stripe_customer_id: Mapped[str | None] = mapped_column(nullable=True)

    # Timestamps managed automatically by the database
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
