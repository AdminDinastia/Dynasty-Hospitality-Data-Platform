from typing import List, Optional, Any

from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.accommodation.accommodation import AccommodationType, CategorySystem


class AccommodationCreate(BaseModel):
    name: str
    type: AccommodationType
    category_system: CategorySystem
    category_value: float
    current_room_count: int
    location: dict[str, Any] | None = None
    tag_ids: Optional[List[int]] = []


# Accommodation Response
class AccommodationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    type: AccommodationType
    category_system: CategorySystem
    category_value: float
    current_room_count: int
    location: dict[str, Any] | None
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = []


# Accommodation Update
class AccommodationUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccommodationType] = None
    category_system: Optional[CategorySystem] = None
    category_value: Optional[float] = None
    current_room_count: Optional[int] = None
    location: dict[str, Any] | None = None
    tag_ids: Optional[List[int]] = []
