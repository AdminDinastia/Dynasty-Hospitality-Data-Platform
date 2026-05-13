import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
    JSON,
)
from sqlalchemy.sql import func
from app.core.database import Base


class RawProductStatus(enum.Enum):
    active = "active"
    inactive = "inactive"


class RawProduct(Base):
    __tablename__ = "raw_products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    # Specific hotel this product refers to
    accommodation_id = Column(Integer, ForeignKey("accommodations.id"), nullable=False)

    # Reference to JSON template in repo
    template_name = Column(String, nullable=False)  # "hotel_report"

    # Partial data shown to non-paying users
    preview_config = Column(JSON, nullable=True)

    # Price in points
    price_points = Column(Integer, nullable=False)

    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    status = Column(
        Enum(RawProductStatus), nullable=False, default=RawProductStatus.active
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
