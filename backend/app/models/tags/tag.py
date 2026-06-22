import enum

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TagCategory(enum.Enum):
    style = "style"
    policty = "policy"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[TagCategory] = mapped_column(Enum(TagCategory), nullable=False)

    accommodations: Mapped[list["Accommodation"]] = relationship(
        "Accommodation", secondary="accommodation_tags", back_populates="tags"
    )
