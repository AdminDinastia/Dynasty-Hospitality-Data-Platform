from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data.dataset import Dataset, DatasetState
from app.schemas.dataset import DatasetUpdate


async def get_dataset(
    session: AsyncSession, dataset_id: int, include_inactive: bool = False
) -> Dataset | None:
    query = select(Dataset).where(Dataset.dataset_id == dataset_id)
    if not include_inactive:
        query = query.where(Dataset.is_active)
    result = await session.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        return None

    return dataset


async def get_datasets(
    session: AsyncSession,
    org_id: int,
    state: DatasetState | None = None,
    accommodation_id: int | None = None,
) -> Sequence[Dataset]:
    query = select(Dataset).where(Dataset.org_id == org_id).where(Dataset.is_active)

    if accommodation_id:
        query = query.where(Dataset.accommodation_id == accommodation_id)

    if state:
        query = query.where(Dataset.state == state)

    result = await session.execute(query)
    datasets = result.scalars().all()

    return datasets


async def update_dataset(session: AsyncSession, data: DatasetUpdate, dataset_id: int):
    query = select(Dataset).where(Dataset.dataset_id == dataset_id)

    result = await session.execute(query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        return None

    if data.is_active is not None:
        dataset.is_active = data.is_active
    await session.commit()
    await session.refresh(dataset)
    return dataset
