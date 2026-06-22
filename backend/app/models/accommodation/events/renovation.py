import enum

from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

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

    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id"), primary_key=True
    )

    renovation_type: Mapped[RenovationType] = mapped_column(Enum(RenovationType))
    renovation_scope: Mapped[RenovationScope] = mapped_column(Enum(RenovationScope))
    cost: Mapped[float] = mapped_column()
