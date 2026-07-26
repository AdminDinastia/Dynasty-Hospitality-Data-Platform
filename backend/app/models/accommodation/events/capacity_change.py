from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.accommodation.events.accommodation_event import (
    AccommodationEvent,
    EventType,
)


class CapacityChange(AccommodationEvent):
    __tablename__ = "capacity_changes"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    old_room_count: Mapped[int] = mapped_column()
    new_room_count: Mapped[int] = mapped_column()

    __mapper_args__ = {
        "polymorphic_identity": EventType.capacity_change,  # discriminator value
    }
