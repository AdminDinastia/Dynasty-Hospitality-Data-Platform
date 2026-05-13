from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class AccommodationTag(Base):
    __tablename__ = "accommodation_tags"

    accommodation_id = Column(
        Integer, ForeignKey("accommodations.id"), primary_key=True
    )

    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
