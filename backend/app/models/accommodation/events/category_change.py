from app.models.accommodation.accommodation import CategorySystem
from app.core.database import Base
from sqlalchemy import Column, Integer, ForeignKey, Enum


class CategoryChange(Base):
    __tablename__ = "category_changes"
    event_id = Column(ForeignKey("accommodation_events.event_id"), primary_key=True)

    old_value = Column(Integer)
    new_value = Column(Integer)

    old_system = Column(Enum(CategorySystem))
    new_system = Column(Enum(CategorySystem))
