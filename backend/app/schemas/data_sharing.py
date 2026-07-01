from typing import Optional
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DataSharingConsentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    consent_id: int
    accommodation_id: int
    allow_raw_sharing: bool
    allow_aggregated: bool
    revenue_share_pct: Decimal
    terms_version: str
    consent_given_at: datetime
    revoked_at: Optional[datetime] = None


class DataSharingUpdate(BaseModel):
    allow_data_sharing: Optional[bool] = None
    allow_aggregated: Optional[bool] = None
