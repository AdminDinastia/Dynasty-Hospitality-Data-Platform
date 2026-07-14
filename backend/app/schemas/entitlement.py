from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.billing.entitlement import EntitlementType


class EntitlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    entitlement_id: int

    org_id: int
    aggregated_product_id: int | None
    raw_product_id: int | None
    entitlement_type: EntitlementType

    granted_at: datetime
    expires_at: datetime | None
    is_active: bool
