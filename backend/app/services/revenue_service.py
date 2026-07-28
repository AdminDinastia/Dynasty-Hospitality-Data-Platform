from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import extract, select
import stripe

from app.models.core.organization import Organization
from app.models.billing.revenue_distribution import (
    RevenueDistribution,
    RevenueDistributionStatus,
)
from app.schemas.revenue import RevenueSummaryResponse


async def handle_connect_webhook(session: AsyncSession, event: stripe.Event):
    if event.type != "account.updated":
        return
    account = event.data.object
    if not account.charges_enabled:
        return

    stripe_account_id = event.account

    query = select(Organization).where(
        Organization.stripe_account_id == stripe_account_id
    )
    result = await session.execute(query)
    org = result.scalar_one_or_none()

    if not org:
        return
    # TODO: Notify the provider his account is verified
    return


async def get_revenue_summary(
    session: AsyncSession, org_id: int
) -> RevenueSummaryResponse:
    query = select(RevenueDistribution).where(RevenueDistribution.org_id == org_id)
    result = await session.execute(query)
    revenue_distributions = result.scalars().all()

    total_earned = 0
    total_paid = 0
    total_pending = 0
    total_distributions = len(revenue_distributions)

    for rv_dist in revenue_distributions:
        total_earned += rv_dist.amount
        if rv_dist.status == RevenueDistributionStatus.paid:
            total_paid += rv_dist.amount
        elif rv_dist.status == RevenueDistributionStatus.pending:
            total_pending += rv_dist.amount

    return RevenueSummaryResponse(
        total_earned=total_earned,
        total_distributions=total_distributions,
        total_paid=total_paid,
        total_pending=total_pending,
    )


async def get_revenue_distributions(
    session: AsyncSession,
    org_id: int,
    status: RevenueDistributionStatus | None = None,
    year: int | None = None,
) -> Sequence[RevenueDistribution]:
    query = select(RevenueDistribution).where(RevenueDistribution.org_id == org_id)

    if status:
        query = query.where(RevenueDistribution.status == status)
    if year:
        query = query.where(extract("year", RevenueDistribution.created_at) == year)

    result = await session.execute(query)
    rev_dists = result.scalars().all()

    return rev_dists


async def get_revenue_distribution(
    session: AsyncSession, distribution_id: int
) -> RevenueDistribution | None:
    query = select(RevenueDistribution).where(
        RevenueDistribution.distribution_id == distribution_id
    )
    result = await session.execute(query)
    rev_dist = result.scalar_one_or_none()

    if not rev_dist:
        return None

    return rev_dist
