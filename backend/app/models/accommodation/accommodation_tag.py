from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AccommodationTag(Base):
    __tablename__ = "accommodation_tags"

    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
