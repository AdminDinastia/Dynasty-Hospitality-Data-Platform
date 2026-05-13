import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
    func,
)
from app.core.database import Base


class AggregatedProductStatus(enum.Enum):
    active = "active"
    inactive = "inactive"


class AggregatedProduct(Base):
    __tablename__ = "aggregated_products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Data source
    aggregation_id = Column(
        Integer, ForeignKey("aggregations.aggregation_id"), nullable=False
    )

    # Template - JSON in repo
    template_name = Column(String, nullable=False)  # "market_report"

    # Monetization
    price_points = Column(Integer, nullable=False)

    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    status = Column(
        Enum(AggregatedProductStatus),
        nullable=False,
        default=AggregatedProductStatus.active,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
