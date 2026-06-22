from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.accommodation.accommodation import AccommodationType
from app.core.database import Base


class TypeChange(Base):
    __tablename__ = "type_changes"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id"), primary_key=True
    )

    old_type: Mapped[AccommodationType] = mapped_column(Enum(AccommodationType))
    new_type: Mapped[AccommodationType] = mapped_column(Enum(AccommodationType))
