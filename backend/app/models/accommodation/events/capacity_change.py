from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CapacityChange(Base):
    __tablename__ = "capacity_changes"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id"), primary_key=True
    )
    old_room_count: Mapped[int] = mapped_column()
    new_room_count: Mapped[int] = mapped_column()
