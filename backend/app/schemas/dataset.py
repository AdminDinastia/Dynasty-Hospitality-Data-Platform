from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.data.dataset import DatasetState


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dataset_id: int
    org_id: int
    accommodation_id: int
    source_upload_id: int | None
    name: str
    period_start: date | None
    period_end: date | None
    granularity: str | None

    currency: str | None
    is_active: bool
    state: DatasetState
    created_at: datetime
    updated_at: datetime


class DatasetUpdate(BaseModel):
    is_active: bool | None
