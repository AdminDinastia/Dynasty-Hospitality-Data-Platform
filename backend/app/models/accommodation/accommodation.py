from typing import Any
import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    ForeignKey,
    DateTime,
    JSON,
    Enum,
    func,
)

from app.core.database import Base
from app.models.accommodation.accommodation_theme import AccommodationTheme
from app.models.accommodation.accommodation_certification import (
    AccommodationCertification,
)


class OwnershipStructure(str, enum.Enum):
    direct_ownership = "direct_ownership"  # owner operates the property directly
    management_contract = (
        "management_contract"  # operated by a brand/operator, owned by a third party
    )
    franchise = "franchise"  # independently owned, operates under a brand franchise
    manchise = "manchise"  # hybrid: management contract that converts to franchise after an initial period, common in Spain
    lease = "lease"  # operator leases the property from the owner
    timeshare = "timeshare"  # fractional/shared ownership
    condo_hotel = "condo_hotel"  # units sold individually, centrally managed


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
    location: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    type: Mapped[AccommodationType] = mapped_column(
        Enum(AccommodationType), nullable=False
    )
    category_system: Mapped[CategorySystem | None] = mapped_column(
        Enum(CategorySystem), nullable=True
    )
    category_value: Mapped[float | None] = mapped_column(nullable=True)
    ownership_structure: Mapped[OwnershipStructure] = mapped_column(
        Enum(OwnershipStructure), nullable=True
    )
    themes: Mapped[list["AccommodationTheme"]] = relationship(
        "AccommodationTheme", cascade="all, delete-orphan"
    )
    certifications: Mapped[list["AccommodationCertification"]] = relationship(
        "AccommodationCertification", cascade="all, delete-orphan"
    )
    current_room_count: Mapped[int | None] = mapped_column(nullable=True)
    building_year: Mapped[int | None] = mapped_column(nullable=True)
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
