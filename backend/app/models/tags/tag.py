import enum
from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
from sqlalchemy.orm import relationship


class TagCategory(enum.Enum):
    style = "style"
    policty = "policy"


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    category = Column(Enum(TagCategory), nullable=False)
    accommodations = relationship(
        "Accommodation", secondary="accommodation_tags", back_populates="tags"
    )
