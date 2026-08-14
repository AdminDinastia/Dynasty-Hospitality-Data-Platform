import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, ForeignKey
from app.core.database import Base


class ThemeType(str, enum.Enum):
    boutique = "boutique"
    spa_wellness = "spa_wellness"
    themed = "themed"
    eco_sustainable = "eco_sustainable"
    bed_and_breakfast = "bed_and_breakfast"
    beach = "beach"
    luxury = "luxury"
    historic_building = "historic_building"
    business = "business"
    family = "family"
    design = "design"
    golf = "golf"
    rural = "rural"
    urban = "urban"
    all_inclusive = "all_inclusive"
    extended_stay = "extended_stay"
    airport = "airport"
    other = "other"


class AccommodationTheme(Base):
    __tablename__ = "accommodation_themes"
    theme_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )
    theme_type: Mapped[ThemeType] = mapped_column(Enum(ThemeType), nullable=False)
