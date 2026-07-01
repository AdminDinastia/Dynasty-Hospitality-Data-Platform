from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.accommodation.accommodation import AccommodationType, CategorySystem


class AccommodationCreate(BaseModel):
    name: str
    city: str
    country: str
    type: AccommodationType
    category_system: CategorySystem
    category_value: float
    current_room_count: int
    tag_ids: Optional[List[int]] = []


# Accommodation Response
class AccommodationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    city: str
    country: str
    type: AccommodationType
    category_system: CategorySystem
    category_value: float
    current_room_count: int
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = []


# Accommodation Update
class AccommodationUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    type: Optional[AccommodationType] = None
    category_system: Optional[CategorySystem] = None
    category_value: Optional[float] = None
    current_room_count: Optional[int] = None
    tag_ids: Optional[List[int]] = []
