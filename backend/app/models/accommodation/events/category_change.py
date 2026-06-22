from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped

from app.models.accommodation.accommodation import CategorySystem
from app.core.database import Base


class CategoryChange(Base):
    __tablename__ = "category_changes"
    event_id: Mapped[int] = mapped_column(
        ForeignKey("accommodation_events.event_id"), primary_key=True
    )

    old_value: Mapped[int] = mapped_column()
    new_value: Mapped[int] = mapped_column()

    old_system: Mapped[CategorySystem] = mapped_column(Enum(CategorySystem))
    new_system: Mapped[CategorySystem] = mapped_column(Enum(CategorySystem))
