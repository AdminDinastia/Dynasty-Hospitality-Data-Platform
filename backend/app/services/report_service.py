from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.accommodation.accommodation import Accommodation

from app.models.billing.entitlement import Entitlement
from app.models.markeplace.raw_product import RawProduct
from app.services import (
    accommodation_data_service,
    accommodation_service,
    event_service,
)


async def get_reports(session: AsyncSession, org_id: int) -> Sequence[Entitlement]:
    active_entitlements_query = (
        select(Entitlement)
        .where(Entitlement.org_id == org_id)
        .where(Entitlement.is_active)
    )
    active_entitlements_result = await session.execute(active_entitlements_query)
    active_entitlements = active_entitlements_result.scalars().all()
    return active_entitlements


async def get_raw_report(session: AsyncSession, entitlement_id: int, org_id: int):
    entitlement_query = select(Entitlement).where(
        Entitlement.entitlement_id == entitlement_id
    )
    entitlement_result = await session.execute(entitlement_query)
    entitlement = entitlement_result.scalar_one_or_none()

    if not entitlement:
        raise HTTPException(404, detail="Entitlement does not exist")

    if entitlement.org_id != org_id:
        raise HTTPException(
            403,
            detail="Entitlement does not grant you access to this organization information.",
        )
    if entitlement.is_active is False:
        raise HTTPException(
            403,
            detail="Entitlement has expired.",
        )

    raw_product_query = select(RawProduct).where(
        RawProduct.product_id == entitlement.raw_product_id
    )
    raw_product_result = await session.execute(raw_product_query)
    raw_product = raw_product_result.scalar_one_or_none()

    if not raw_product:
        raise HTTPException(404, detail="Raw Product does not exist")

    if raw_product.is_active is False:
        raise HTTPException(
            403,
            detail="Raw Product has expired or deactivated.",
        )

    accommodation_query = select(Accommodation).where(
        Accommodation.id == raw_product.accommodation_id
    )
    accommodation_result = await session.execute(accommodation_query)
    accommodation = accommodation_result.scalar_one_or_none()

    if not accommodation:
        raise HTTPException(404, detail="Accommodation does not exist")

    if accommodation.is_active is False:
        raise HTTPException(
            403,
            detail="Accommodation has expired or deactivated.",
        )
    # Extended Data
    room_types = await accommodation_service.get_room_types(
        session=session, accommodation_id=accommodation.id
    )
    distribution_channels = await accommodation_service.get_distribution_channels(
        session=session,
        accommodation_id=accommodation.id,
        year=raw_product.year,
        include_historical=True,
    )
    revenue_breakdowns = await accommodation_service.get_revenue_breakdowns(
        session=session,
        accommodation_id=accommodation.id,
        year=raw_product.year,
        include_historical=True,
    )
    accommodation_details = await accommodation_service.get_accommodation_details(
        session=session,
        accommodation_id=accommodation.id,
        year=raw_product.year,
        include_historical=True,
    )
    events = await event_service.get_events(
        session=session, accommodation_id=accommodation.id
    )

    # Search Datasets
    datasets = await accommodation_data_service.get_datasets(
        session=session,
        org_id=org_id,
        year=raw_product.year,
        accommodation_id=accommodation.id,
    )


async def get_aggregated_report(
    session: AsyncSession, entitlement_id: int, org_id: int
):
    # Construct AggregatedReportResponse
    pass
