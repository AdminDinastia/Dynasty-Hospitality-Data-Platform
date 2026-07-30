from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, JSON

from app.core.database import Base


class AccommodationDetails(Base):
    __tablename__ = "accommodation_details"
    detail_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE")
    )
    year: Mapped[int] = mapped_column(nullable=False)
    lead_time_days: Mapped[int | None] = mapped_column(nullable=True)
    length_of_stay: Mapped[float | None] = mapped_column(nullable=True)
    cpor: Mapped[float | None] = mapped_column(nullable=True)
    employee_count: Mapped[int | None] = mapped_column(nullable=True)
