from typing import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data.accommodation_data import AccommodationData, AccommodationDataState
from app.schemas.accommodation_data import AccommodationDataUpdate


async def get_dataset(
    session: AsyncSession, accommodation_data_id: int, include_inactive: bool = False
) -> AccommodationData | None:
    query = select(AccommodationData).where(
        AccommodationData.accommodation_data_id == accommodation_data_id
    )
    if not include_inactive:
        query = query.where(AccommodationData.is_active)
    result = await session.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        return None

    return dataset


async def get_datasets(
    session: AsyncSession,
    org_id: int,
    year: int | None = None,
    state: AccommodationDataState | None = None,
    accommodation_id: int | None = None,
    include_historical: bool = False,
) -> Sequence[AccommodationData]:
    query = (
        select(AccommodationData)
        .where(AccommodationData.org_id == org_id)
        .where(AccommodationData.is_active)
    )

    if accommodation_id:
        query = query.where(AccommodationData.accommodation_id == accommodation_id)

    if state:
        query = query.where(AccommodationData.state == state)

    if year:
        if include_historical:
            query = query.where(AccommodationData.year <= year)
        else:
            query = query.where(AccommodationData.year == year)

    result = await session.execute(query)
    datasets = result.scalars().all()

    return datasets


async def update_dataset(
    session: AsyncSession, data: AccommodationDataUpdate, accommodation_data_id: int
):
    query = select(AccommodationData).where(
        AccommodationData.accommodation_data_id == accommodation_data_id
    )

    result = await session.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        return None

    if data.is_active is not None:
        dataset.is_active = data.is_active
        if not data.is_active:
            dataset.deleted_at = datetime.now(timezone.utc)
        else:
            dataset.deleted_at = None

    await session.commit()
    await session.refresh(dataset)
    return dataset
