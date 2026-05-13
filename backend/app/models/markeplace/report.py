import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, Enum
from sqlalchemy.sql import func
from app.core.database import Base


class MarketReport(Base):
    __tablename__ = "market_reports"

    report_id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)
    aggregated_product_id = Column(
        Integer, ForeignKey("aggregated_products.product_id"), nullable=False
    )

    # Saved filters for easy repeat queries
    filters = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AccommodationReport(Base):
    __tablename__ = "accommodation_reports"

    report_id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)
    raw_product_id = Column(
        Integer, ForeignKey("raw_products.product_id"), nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
