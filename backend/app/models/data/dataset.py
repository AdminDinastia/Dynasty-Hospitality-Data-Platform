import enum
from app.core.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Boolean,
    Enum,
    DateTime,
    func,
)


class DatasetState(enum.Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"


class Dataset(Base):
    __tablename__ = "datasets"

    dataset_id = Column(Integer, primary_key=True)
    org_id = Column(ForeignKey("organizations.org_id"), nullable=False)
    accommodation_id = Column(Integer, ForeignKey("accommodations.id"), nullable=False)

    source_upload_id = Column(ForeignKey("uploads.upload_id"), nullable=True)

    name = Column(String, nullable=False)

    granularity = Column(String)  # flexible

    period_start = Column(Date)
    period_end = Column(Date)

    storage_path = Column(String, nullable=False)

    currency = Column(String, nullable=True)  # optional

    is_active = Column(Boolean, default=True)

    state = Column(Enum(DatasetState), nullable=False, default="draft")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
