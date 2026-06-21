from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class DataSharingConsentResponse(BaseModel):
    consent_id: int
    accommodation_id: int
    allow_raw_sharing: bool
    allow_aggregated: bool
    revenue_share_pct: float
    terms_version: str
    consent_given_at: datetime
    revoked_at: Optional[datetime]


class DataSharingUpdate(BaseModel):
    allow_data_sharing: Optional[bool] = None
    allow_aggregated: Optional[bool] = None
