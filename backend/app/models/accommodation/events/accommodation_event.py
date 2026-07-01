import enum
from datetime import datetime, date

from sqlalchemy import DateTime, Enum, ForeignKey, func, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EventType(str, enum.Enum):
    renovation = "renovation"
    category_change = "category_change"
    capacity_change = "capacity_change"
    type_change = "type_change"
    created = "created"


class AccommodationEvent(Base):
    __tablename__ = "accommodation_events"
    __mapper_args__ = {
        "polymorphic_on": "event_type",
        "polymorphic_identity": None,
    }

    event_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE")
    )

    event_type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
