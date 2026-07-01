from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.accommodation.accommodation import AccommodationType
from app.models.accommodation.events.accommodation_event import (
    AccommodationEvent,
    EventType,
)


class TypeChange(AccommodationEvent):
    __tablename__ = "type_changes"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )

    old_type: Mapped[AccommodationType] = mapped_column(Enum(AccommodationType))
    new_type: Mapped[AccommodationType] = mapped_column(Enum(AccommodationType))

    __mapper_args__ = {
        "polymorphic_identity": EventType.type_change,  # discriminator value
    }
