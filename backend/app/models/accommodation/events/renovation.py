import enum
from sqlalchemy import Column, ForeignKey, Float, Enum
from app.core.database import Base


class RenovationType(enum.Enum):
    partial = "partial"
    full = "full"


class RenovationScope(enum.Enum):
    rooms = "rooms"
    common_areas = "common_areas"
    amenities = "amenities"
    structural = "structural"
    full_property = "full_property"


class Renovation(Base):
    __tablename__ = "renovations"

    event_id = Column(ForeignKey("accommodation_events.event_id"), primary_key=True)

    renovation_type = Column(Enum(RenovationType))
    renovation_scope = Column(Enum(RenovationScope))
    cost = Column(Float)
