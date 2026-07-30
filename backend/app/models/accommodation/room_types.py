import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum


from app.core.database import Base


class RoomCategory(str, enum.Enum):
    single = "single"
    double = "double"
    twin = "twin"
    triple = "triple"
    quadruple = "quadruple"
    suite = "suite"
    junior_suite = "junior_suite"
    studio = "studio"
    apartment = "apartment"
    family = "family"
    accessible = "accessible"
    penthouse = "penthouse"
    bunk = "bunk"


class RoomLevel(str, enum.Enum):
    standard = "standard"
    superior = "superior"
    deluxe = "deluxe"
    executive = "executive"
    luxury = "luxury"
    presidential = "presidential"


class RoomType(Base):
    __tablename__ = "room_types"

    room_type_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[RoomCategory] = mapped_column(Enum(RoomCategory), nullable=False)
    level: Mapped[RoomLevel] = mapped_column(Enum(RoomLevel), nullable=False)
    custom_name: Mapped[str | None] = mapped_column(nullable=True)
    count: Mapped[int] = mapped_column(nullable=False)
