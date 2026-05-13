from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey


class CapacityChange(Base):
    __tablename__ = "capacity_changes"

    event_id = Column(ForeignKey("accommodation_events.event_id"), primary_key=True)
    old_room_count = Column(Integer)
    new_room_count = Column(Integer)
