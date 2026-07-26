from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.billing.points_ledger import PointsReason


class PointsBalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    org_id: int
    points_balance: int


class PointsHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ledger_id: int
    points: int
    reason: PointsReason
    reference_id: int | None
    reference_type: str | None
    created_at: datetime


class PointsPurchaseRequest(BaseModel):
    amount: float


class PointsPurchaseResponse(BaseModel):
    checkout_url: str
