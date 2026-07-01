from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped


from app.models.accommodation.events.accommodation_event import (
    AccommodationEvent,
    EventType,
)
from app.models.accommodation.accommodation import AccommodationType, CategorySystem


class CreationEvent(AccommodationEvent):
    __tablename__ = "creation_events"
    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )
    initial_type: Mapped[AccommodationType] = mapped_column(Enum(AccommodationType))
    initial_category_system: Mapped[CategorySystem] = mapped_column(
        Enum(CategorySystem)
    )
    initial_category_value: Mapped[float] = mapped_column()
    initial_room_count: Mapped[int] = mapped_column()

    __mapper_args__ = {
        "polymorphic_identity": EventType.created,
    }
