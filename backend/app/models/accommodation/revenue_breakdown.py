import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum
from app.core.database import Base


class RevenueDepartment(str, enum.Enum):
    rooms = "rooms"
    food_and_beverage = "food_and_beverage"
    spa = "spa"
    meetings_events = "meetings_events"
    parking = "parking"
    laundry = "laundry"
    minibar = "minibar"
    activities = "activities"
    other = "other"


class RevenueBreakdown(Base):
    __tablename__ = "revenue_breakdowns"
    breakdown_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(nullable=False)
    department: Mapped[RevenueDepartment] = mapped_column(
        Enum(RevenueDepartment), nullable=False
    )
    revenue: Mapped[float] = mapped_column(nullable=False)
