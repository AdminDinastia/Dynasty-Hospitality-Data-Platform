import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    func,
    null,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class AccommodationType(enum.Enum):
    hotel = "hotel"
    hostel = "hostel"
    aparthotel = "aparthotel"
    resort = "resort"


class CategorySystem(enum.Enum):
    stars = "stars"
    keys = "keys"


class Accommodation(Base):
    __tablename__ = "accommodations"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"))

    name = Column(String, nullable=False)
    city = Column(String)
    country = Column(String)

    type = Column(Enum(AccommodationType), nullable=False)
    category_system = Column(Enum(CategorySystem), nullable=True)
    category_value = Column(Integer, nullable=True)

    tags = relationship(
        "Tag", secondary="accommodation_tags", back_populates="accommodations"
    )

    current_room_count = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
