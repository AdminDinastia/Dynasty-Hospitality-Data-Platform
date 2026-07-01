from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped

from app.models.accommodation.accommodation import CategorySystem

from app.models.accommodation.events.accommodation_event import (
    AccommodationEvent,
    EventType,
)


class CategoryChange(AccommodationEvent):
    __tablename__ = "category_changes"
    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id", ondelete="CASCADE"),
        primary_key=True,
    )

    old_value: Mapped[float] = mapped_column()
    new_value: Mapped[float] = mapped_column()

    old_system: Mapped[CategorySystem] = mapped_column(Enum(CategorySystem))
    new_system: Mapped[CategorySystem] = mapped_column(Enum(CategorySystem))

    __mapper_args__ = {
        "polymorphic_identity": EventType.category_change,  # discriminator value
    }
