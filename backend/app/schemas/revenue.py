import decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.billing.revenue_distribution import RevenueDistributionStatus


class RevenueDistributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    distribution_id: int
    raw_product_id: int
    buyer_org_id: int
    org_id: int
    accommodation_id: int
    amount: int
    revenue_share_pct: decimal.Decimal
    stripe_transfer_id: str | None
    status: RevenueDistributionStatus
    created_at: datetime
    updated_at: datetime


class RevenueSummaryResponse(BaseModel):
    total_earned: int
    total_distributions: int
    total_paid: int
    total_pending: int


class RevenueDistributionFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: RevenueDistributionStatus | None = None
    year: int | None = None
