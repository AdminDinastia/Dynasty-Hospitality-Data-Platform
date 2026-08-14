from typing import Optional, Any

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.accommodation.accommodation import (
    AccommodationType,
    CategorySystem,
    OwnershipStructure,
)


class Location(BaseModel):
    country: str
    city: str
    nuts1: str
    nuts2: str
    nuts3: str
    lat: float
    lon: float


class LocationCreate(BaseModel):
    country: str
    city: str
    nuts3: str
    lat: float
    lon: float


class AccommodationCreate(BaseModel):
    name: str
    type: AccommodationType
    category_system: CategorySystem
    category_value: float
    current_room_count: int
    location: LocationCreate
    building_year: int
    ownership_structure: OwnershipStructure


# Accommodation Response
class AccommodationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    type: AccommodationType
    ownership_structure: OwnershipStructure
    category_system: CategorySystem
    category_value: float
    current_room_count: int
    location: Location
    building_year: int
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime


# Accommodation Update
class AccommodationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccommodationType] = None
    ownership_structure: OwnershipStructure | None = None
    category_system: Optional[CategorySystem] = None
    category_value: Optional[float] = None
    current_room_count: Optional[int] = None
    location: LocationCreate | None = None
    building_year: int | None = None
