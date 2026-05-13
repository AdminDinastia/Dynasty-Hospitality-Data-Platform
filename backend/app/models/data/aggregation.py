import enum
from app.core.database import Base
from sqlalchemy import Column, Integer, String, JSON, Enum, DateTime, func


class AggregationStatus(enum.Enum):
    pending = "pending"
    computing = "computing"
    ready = "ready"
    failed = "failed"


class Aggregation(Base):
    __tablename__ = "aggregations"

    aggregation_id = Column(Integer, primary_key=True)

    aggregation_type = Column(String, nullable=False)  # 'location', 'category'...
    parameters = Column(JSON, nullable=False)
    # {"level": "city", "location": "Gran Canaria"}

    storage_path = Column(String, nullable=True)
    status = Column(
        Enum(AggregationStatus), nullable=False, default=AggregationStatus.pending
    )
    computed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
