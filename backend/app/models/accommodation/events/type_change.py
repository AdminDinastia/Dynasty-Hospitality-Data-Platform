from app.models.accommodation.accommodation import AccommodationType
from app.core.database import Base
from sqlalchemy import Column, Enum, ForeignKey


class TypeChange(Base):
    __tablename__ = "type_changes"

    event_id = Column(ForeignKey("accommodation_events.event_id"), primary_key=True)

    old_type = Column(Enum(AccommodationType))
    new_type = Column(Enum(AccommodationType))
