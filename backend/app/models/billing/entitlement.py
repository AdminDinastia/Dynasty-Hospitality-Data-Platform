import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base


class EntitlementType(enum.Enum):
    points = "points"  # paid with points (aggregated)
    granted = "granted"  # manually granted by platform


class Entitlement(Base):
    __tablename__ = "entitlements"

    entitlement_id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)

    # One of the two depending on product type
    aggregated_product_id = Column(
        Integer, ForeignKey("aggregated_products.product_id"), nullable=True
    )
    raw_product_id = Column(
        Integer, ForeignKey("raw_products.product_id"), nullable=True
    )

    entitlement_type = Column(Enum(EntitlementType), nullable=False)

    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
