import enum
from sqlalchemy import Column, DateTime, Integer, String, Enum, ForeignKey, func
from app.core.database import Base


class EventType(enum.Enum):
    renovation = "renovation"
    category_change = "category_change"
    capacity_change = "capacity_change"
    type_change = "type_change"


class AccommodationEvent(Base):
    __tablename__ = "accommodation_events"

    event_id = Column(Integer, primary_key=True)
    accommodation_id = Column(Integer, ForeignKey("accommodations.id"))
    event_type = Column(Enum(EventType), nullable=False)
    effective_date = Column(DateTime)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), onupdate=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
