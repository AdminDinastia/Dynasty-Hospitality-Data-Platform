from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.data.accommodation_data import AccommodationDataState, GranularityType


class AccommodationDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accommodation_data_id: int
    org_id: int
    accommodation_id: int
    raw_product_id: int | None
    source_upload_id: int | None
    granularity: GranularityType | None
    name: str
    period_start: date | None
    period_end: date | None

    currency: str | None
    is_active: bool
    deleted_at: datetime | None
    state: AccommodationDataState
    created_at: datetime
    updated_at: datetime


class AccommodationDataUpdate(BaseModel):
    is_active: bool | None
