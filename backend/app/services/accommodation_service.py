from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tags.tag import Tag
from app.models.accommodation.accommodation import Accommodation
from app.services import data_sharing_service

from app.schemas.accommodation import AccommodationCreate, AccommodationUpdate
from app.services import event_service


async def create_accommodation(
    session: AsyncSession,
    data: AccommodationCreate,
    org_id: int,
) -> Accommodation:
    query = select(Tag).where(Tag.id.in_(data.tag_ids))
    result = await session.execute(query)
    tags = result.scalars().all()

    new_accommodation = Accommodation(
        name=data.name,
        org_id=org_id,
        city=data.city,
        country=data.country,
        type=data.type,
        category_system=data.category_system,
        category_value=data.category_value,
        tags=tags,
        current_room_count=data.current_room_count,
    )
    session.add(new_accommodation)
    await session.flush()

    await data_sharing_service.create_consent(session, new_accommodation.id)

    await session.commit()
    await event_service.create_creation_event(session, new_accommodation)

    return new_accommodation


async def get_accommodations(
    session: AsyncSession,
    org_id: int,
) -> Sequence[Accommodation]:
    query = (
        select(Accommodation)
        .where(Accommodation.org_id == org_id)
        .options(selectinload(Accommodation.tags))
    )
    result = await session.execute(query)
    accommodations = result.scalars().all()

    return accommodations


async def get_accommodation(
    session: AsyncSession,
    accommodation_id: int,
) -> Accommodation | None:
    query = (
        select(Accommodation)
        .where(Accommodation.id == accommodation_id)
        .options(selectinload(Accommodation.tags))
    )
    result = await session.execute(query)
    accommodation = result.scalar_one_or_none()

    return accommodation


async def update_accommodation(
    session: AsyncSession, accommodation_id: int, data: AccommodationUpdate
) -> Accommodation | None:
    query = (
        select(Accommodation)
        .where(Accommodation.id == accommodation_id)
        .options(selectinload(Accommodation.tags))
    )
    result = await session.execute(query)
    accommodation = result.scalar_one_or_none()

    if not accommodation:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "tag_ids" in update_data:
        tag_ids = update_data.pop("tag_ids")
        tags_query = select(Tag).where(Tag.id.in_(tag_ids))
        tags_result = await session.execute(tags_query)
        accommodation.tags = list(tags_result.scalars().all())

    for field, value in update_data.items():
        setattr(accommodation, field, value)

    await session.commit()
    return accommodation


async def delete_accommodation(session: AsyncSession, accommodation_id: int) -> bool:
    query = select(Accommodation).where(Accommodation.id == accommodation_id)
    result = await session.execute(query)
    accommodation = result.scalar_one_or_none()

    if not accommodation:
        return False

    await session.delete(accommodation)
    await session.commit()
    return True
