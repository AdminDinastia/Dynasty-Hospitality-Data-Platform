from typing import Literal, Annotated, Union
from datetime import date, datetime

from app.models.accommodation.events.renovation import RenovationType, RenovationScope
from app.models.accommodation.events.category_change import CategorySystem
from app.models.accommodation.events.type_change import AccommodationType


from pydantic import BaseModel, ConfigDict, Field


class BaseEventCreate(BaseModel):
    effective_date: date
    description: str | None = None


class CapacityChangeCreate(BaseEventCreate):
    event_type: Literal["capacity_change"] = "capacity_change"
    old_room_count: int
    new_room_count: int


class CategoryChangeCreate(BaseEventCreate):
    event_type: Literal["category_change"] = "category_change"

    old_value: float
    new_value: float

    old_system: CategorySystem
    new_system: CategorySystem


class RenovationChangeCreate(BaseEventCreate):
    event_type: Literal["renovation"] = "renovation"
    renovation_type: RenovationType
    renovation_scope: RenovationScope
    cost: float


class TypeChangeCreate(BaseEventCreate):
    event_type: Literal["type_change"] = "type_change"
    old_type: AccommodationType
    new_type: AccommodationType


EventCreate = Annotated[
    Union[
        CapacityChangeCreate,
        CategoryChangeCreate,
        RenovationChangeCreate,
        TypeChangeCreate,
    ],
    Field(discriminator="event_type"),
]


class BaseEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_id: int
    accommodation_id: int
    effective_date: date
    description: str | None
    created_at: datetime


class CapacityChangeResponse(BaseEventResponse):
    event_type: Literal["capacity_change"] = "capacity_change"
    old_room_count: int
    new_room_count: int


class CategoryChangeResponse(BaseEventResponse):
    event_type: Literal["category_change"] = "category_change"
    old_value: float
    new_value: float

    old_system: CategorySystem
    new_system: CategorySystem


class RenovationChangeResponse(BaseEventResponse):
    event_type: Literal["renovation"] = "renovation"
    renovation_type: RenovationType
    renovation_scope: RenovationScope
    cost: float


class TypeChangeResponse(BaseEventResponse):
    event_type: Literal["type_change"] = "type_change"
    old_type: AccommodationType
    new_type: AccommodationType


class CreationEventResponse(BaseEventResponse):
    event_type: Literal["created"] = "created"
    initial_type: AccommodationType
    initial_category_system: CategorySystem
    initial_category_value: float
    initial_room_count: int


class BaseEventUpdate(BaseModel):
    effective_date: date | None = None
    description: str | None = None


class CapacityChangeUpdate(BaseEventUpdate):
    event_type: Literal["capacity_change"] = "capacity_change"
    old_room_count: int | None = None
    new_room_count: int | None = None


class CategoryChangeUpdate(BaseEventUpdate):
    event_type: Literal["category_change"] = "category_change"

    old_value: float | None = None
    new_value: float | None = None

    old_system: CategorySystem | None = None
    new_system: CategorySystem | None = None


class RenovationChangeUpdate(BaseEventUpdate):
    event_type: Literal["renovation"] = "renovation"
    renovation_type: RenovationType | None = None
    renovation_scope: RenovationScope | None = None
    cost: float | None = None


class TypeChangeUpdate(BaseEventUpdate):
    event_type: Literal["type_change"] = "type_change"
    old_type: AccommodationType | None = None
    new_type: AccommodationType | None = None


class CreationEventUpdate(BaseEventUpdate):
    event_type: Literal["created"] = "created"
    initial_type: AccommodationType | None = None
    initial_category_system: CategorySystem | None = None
    initial_category_value: float | None = None
    initial_room_count: int | None = None


EventCreate = Annotated[
    Union[
        CapacityChangeCreate,
        CategoryChangeCreate,
        RenovationChangeCreate,
        TypeChangeCreate,
    ],
    Field(discriminator="event_type"),
]


EventUpdate = Annotated[
    Union[
        CapacityChangeUpdate,
        CategoryChangeUpdate,
        RenovationChangeUpdate,
        TypeChangeUpdate,
        CreationEventUpdate,
    ],
    Field(discriminator="event_type"),
]
