from typing import Annotated, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, HTTPException

from app.models.core.user import User, UserRole
from app.core.dependencies import get_db, get_current_user
from app.schemas.revenue import (
    RevenueSummaryResponse,
    RevenueDistributionResponse,
    RevenueDistributionFilters,
)

from app.services import revenue_service

router = APIRouter(prefix="/revenue")


@router.get("/summary")
async def get_revenue_summary(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> RevenueSummaryResponse:
    if user.role != UserRole.org_admin:
        raise HTTPException(403, detail="Only org admins can access this information.")

    if not user.org_id:
        raise HTTPException(403, detail="User does not belong to an organization.")

    rev_summary = await revenue_service.get_revenue_summary(
        session=session, org_id=user.org_id
    )
    return rev_summary


@router.get("/distributions")
async def get_revenue_distributions(
    filters: Annotated[RevenueDistributionFilters, Query()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Sequence[RevenueDistributionResponse]:
    if user.role != UserRole.org_admin:
        raise HTTPException(status_code=403, detail="Only org admins can access this.")
    if not user.org_id:
        raise HTTPException(
            status_code=403, detail="User does not belong to an organization."
        )
    rev_dists = await revenue_service.get_revenue_distributions(
        session=session, org_id=user.org_id, status=filters.status, year=filters.year
    )
    return [RevenueDistributionResponse.model_validate(rd) for rd in rev_dists]


@router.get("/distributions/{distribution_id}")
async def get_revenue_distribution(
    distribution_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RevenueDistributionResponse:
    if not user.org_id:
        raise HTTPException(
            status_code=403, detail="User does not belong to an organization."
        )
    rev_dist = await revenue_service.get_revenue_distribution(
        session=session, distribution_id=distribution_id
    )
    if not rev_dist:
        raise HTTPException(status_code=404, detail="Distribution not found.")
    if rev_dist.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    return RevenueDistributionResponse.model_validate(rev_dist)
