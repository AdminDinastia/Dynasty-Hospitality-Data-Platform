import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    ForeignKey,
    DateTime,
    Enum,
    func,
)

from app.core.database import Base
from app.models.tags.tag import Tag


class AccommodationType(str, enum.Enum):
    hotel = "hotel"
    hostel = "hostel"
    aparthotel = "aparthotel"
    resort = "resort"


class CategorySystem(str, enum.Enum):
    stars = "stars"
    keys = "keys"


class Accommodation(Base):
    __tablename__ = "accommodations"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.org_id"))
    name: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    type: Mapped[AccommodationType] = mapped_column(
        Enum(AccommodationType), nullable=False
    )
    category_system: Mapped[CategorySystem | None] = mapped_column(
        Enum(CategorySystem), nullable=True
    )
    category_value: Mapped[float | None] = mapped_column(nullable=True)
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="accommodation_tags", back_populates="accommodations"
    )
    current_room_count: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(
        default=True, nullable=False, server_default="true"
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
