from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectin_polymorphic
from fastapi import HTTPException

from app.models.accommodation.accommodation import Accommodation
from app.schemas.event import (
    CapacityChangeUpdate,
    CategoryChangeUpdate,
    CreationEventUpdate,
    RenovationChangeUpdate,
    TypeChangeUpdate,
    CapacityChangeCreate,
    CategoryChangeCreate,
    RenovationChangeCreate,
    TypeChangeCreate,
)

from app.models.accommodation.events.accommodation_event import AccommodationEvent
from app.models.accommodation.events.accommodation_event import EventType
from app.models.accommodation.events.category_change import CategoryChange
from app.models.accommodation.events.capacity_change import CapacityChange
from app.models.accommodation.events.renovation import Renovation
from app.models.accommodation.events.type_change import TypeChange
from app.models.accommodation.events.creation_event import CreationEvent
from app.services import accommodation_service


async def create_creation_event(
    session: AsyncSession, accommodation: Accommodation
) -> CreationEvent:
    new_creation_event = CreationEvent(
        accommodation_id=accommodation.id,
        effective_date=accommodation.created_at.date(),
        initial_type=accommodation.type,
        initial_category_system=accommodation.category_system,
        initial_category_value=accommodation.category_value,
        initial_room_count=accommodation.current_room_count,
    )
    session.add(new_creation_event)

    await session.commit()
    return new_creation_event


async def create_capacity_change(
    session: AsyncSession, accommodation_id: int, data: CapacityChangeCreate
) -> CapacityChange:
    new_capacity_change = CapacityChange(
        accommodation_id=accommodation_id,
        effective_date=data.effective_date,
        description=data.description,
        old_room_count=data.old_room_count,
        new_room_count=data.new_room_count,
    )
    session.add(new_capacity_change)

    accommodation = await accommodation_service.get_accommodation(
        session=session, accommodation_id=accommodation_id
    )
    if accommodation:
        accommodation.current_room_count = data.new_room_count

    await session.commit()
    return new_capacity_change


async def create_renovation(
    session: AsyncSession, accommodation_id: int, data: RenovationChangeCreate
) -> Renovation:
    new_renovation = Renovation(
        accommodation_id=accommodation_id,
        effective_date=data.effective_date,
        description=data.description,
        renovation_type=data.renovation_type,
        renovation_scope=data.renovation_scope,
        cost=data.cost,
    )

    session.add(new_renovation)
    await session.commit()
    return new_renovation


async def create_category_change(
    session: AsyncSession, accommodation_id: int, data: CategoryChangeCreate
) -> CategoryChange:
    new_category_change = CategoryChange(
        accommodation_id=accommodation_id,
        effective_date=data.effective_date,
        description=data.description,
        old_value=data.old_value,
        new_value=data.new_value,
        old_system=data.old_system,
        new_system=data.new_system,
    )
    session.add(new_category_change)

    accommodation = await accommodation_service.get_accommodation(
        session=session, accommodation_id=accommodation_id
    )
    if accommodation:
        accommodation.category_value = data.new_value
        accommodation.category_system = data.new_system

    await session.commit()

    return new_category_change


async def create_type_change(
    session: AsyncSession, accommodation_id: int, data: TypeChangeCreate
) -> TypeChange:
    new_type_change = TypeChange(
        accommodation_id=accommodation_id,
        effective_date=data.effective_date,
        description=data.description,
        old_type=data.old_type,
        new_type=data.new_type,
    )

    session.add(new_type_change)

    accommodation = await accommodation_service.get_accommodation(
        session=session, accommodation_id=accommodation_id
    )
    if accommodation:
        accommodation.type = data.new_type
    await session.commit()
    return new_type_change


async def get_events(
    session: AsyncSession,
    accommodation_id: int,
    event_type: EventType | None = None,
) -> Sequence[AccommodationEvent]:
    query = (
        select(AccommodationEvent)
        .where(AccommodationEvent.accommodation_id == accommodation_id)
        .options(
            selectin_polymorphic(
                AccommodationEvent,
                [CapacityChange, TypeChange, CategoryChange, Renovation, CreationEvent],
            )
        )
    )
    if event_type:
        query = query.where(AccommodationEvent.event_type == event_type)

    result = await session.execute(query)
    events = result.scalars().all()

    return events


async def get_event(
    session: AsyncSession,
    accommodation_id: int,
    event_id: int,
) -> AccommodationEvent:
    query = select(AccommodationEvent).where(
        AccommodationEvent.accommodation_id == accommodation_id
    )
    query = query.where(AccommodationEvent.event_id == event_id).options(
        selectin_polymorphic(
            AccommodationEvent,
            [TypeChange, Renovation, CategoryChange, CapacityChange, CreationEvent],
        )
    )

    result = await session.execute(query)
    event = result.scalar_one_or_none()

    return event


async def _is_latest_event(
    session: AsyncSession,
    event: AccommodationEvent,
) -> bool:
    query = (
        select(AccommodationEvent)
        .where(AccommodationEvent.accommodation_id == event.accommodation_id)
        .where(AccommodationEvent.event_type == event.event_type)
        .order_by(AccommodationEvent.effective_date.desc())
        .limit(1)
    )
    result = await session.execute(query)
    latest = result.scalar_one_or_none()
    return latest is not None and latest.event_id == event.event_id


async def update_creation_event(
    session: AsyncSession, event_id: int, data: CreationEventUpdate
) -> CreationEvent | None:
    query = select(CreationEvent).where(CreationEvent.event_id == event_id)
    result = await session.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        return None

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("event_type", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    if await _is_latest_event(session=session, event=event):
        accommodation = await accommodation_service.get_accommodation(
            session=session, accommodation_id=event.accommodation_id
        )
        if accommodation:
            if data.initial_type is not None:
                accommodation.type = data.initial_type
            if data.initial_category_system is not None:
                accommodation.category_system = data.initial_category_system
            if data.initial_category_value is not None:
                accommodation.category_value = data.initial_category_value
            if data.initial_room_count is not None:
                accommodation.current_room_count = data.initial_room_count

    await session.commit()
    return event


async def update_capacity_change(
    session: AsyncSession,
    event_id: int,
    data: CapacityChangeUpdate,
) -> CapacityChange | None:
    query = select(CapacityChange).where(CapacityChange.event_id == event_id)
    result = await session.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        return None

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("event_type", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    if await _is_latest_event(session=session, event=event):
        accommodation = await accommodation_service.get_accommodation(
            session=session, accommodation_id=event.accommodation_id
        )
        if accommodation:
            if data.new_room_count is not None:
                accommodation.current_room_count = data.new_room_count

    await session.commit()
    return event


async def update_renovation(
    session: AsyncSession,
    event_id: int,
    data: RenovationChangeUpdate,
) -> Renovation | None:
    query = select(Renovation).where(Renovation.event_id == event_id)
    result = await session.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        return None

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("event_type", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    await session.commit()
    return event


async def update_category_change(
    session: AsyncSession,
    event_id: int,
    data: CategoryChangeUpdate,
) -> CategoryChange | None:
    query = select(CategoryChange).where(CategoryChange.event_id == event_id)
    result = await session.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        return None

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("event_type", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    if await _is_latest_event(session=session, event=event):
        accommodation = await accommodation_service.get_accommodation(
            session=session, accommodation_id=event.accommodation_id
        )
        if accommodation:
            if data.new_value is not None:
                accommodation.category_value = data.new_value
            if data.new_system is not None:
                accommodation.category_system = data.new_system

    await session.commit()
    return event


async def update_type_change(
    session: AsyncSession,
    event_id: int,
    data: TypeChangeUpdate,
) -> TypeChange | None:
    query = select(TypeChange).where(TypeChange.event_id == event_id)
    result = await session.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        return None

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("event_type", None)

    for field, value in update_data.items():
        setattr(event, field, value)

    if await _is_latest_event(session=session, event=event):
        accommodation = await accommodation_service.get_accommodation(
            session=session, accommodation_id=event.accommodation_id
        )
        if accommodation:
            if data.new_type is not None:
                accommodation.type = data.new_type

    await session.commit()
    return event


async def delete_event(
    session: AsyncSession,
    accommodation_id: int,
    event_id: int,
) -> bool:
    query = select(AccommodationEvent).where(
        AccommodationEvent.accommodation_id == accommodation_id
    )
    query = query.where(AccommodationEvent.event_id == event_id)

    result = await session.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        return False

    if event.event_type == EventType.created:
        raise HTTPException(status_code=403, detail="Creation event cannot be deleted.")

    if await _is_latest_event(session=session, event=event):
        query = (
            select(AccommodationEvent)
            .where(AccommodationEvent.accommodation_id == event.accommodation_id)
            .where(AccommodationEvent.event_type == event.event_type)
            .where(AccommodationEvent.event_id != event.event_id)
            .order_by(AccommodationEvent.effective_date.desc())
            .limit(1)
            .options(
                selectin_polymorphic(
                    AccommodationEvent,
                    [
                        CapacityChange,
                        TypeChange,
                        CategoryChange,
                        Renovation,
                        CreationEvent,
                    ],
                )
            )
        )
        result = await session.execute(query)
        previous_event = result.scalar_one_or_none()

        if previous_event:
            accommodation = await accommodation_service.get_accommodation(
                session=session, accommodation_id=accommodation_id
            )
            if accommodation:
                if isinstance(previous_event, CapacityChange):
                    accommodation.current_room_count = previous_event.new_room_count
                elif isinstance(previous_event, TypeChange):
                    accommodation.type = previous_event.new_type
                elif isinstance(previous_event, CategoryChange):
                    accommodation.category_value = previous_event.new_value
                    accommodation.category_system = previous_event.new_system
                elif isinstance(previous_event, CreationEvent):
                    accommodation.current_room_count = previous_event.initial_room_count
                    accommodation.type = previous_event.initial_type
                    accommodation.category_value = previous_event.initial_category_value
                    accommodation.category_system = (
                        previous_event.initial_category_system
                    )
        else:
            creation_query = select(CreationEvent).where(
                CreationEvent.accommodation_id == accommodation_id
            )
            creation_result = await session.execute(creation_query)
            creation_event = creation_result.scalar_one_or_none()
            if creation_event:
                accommodation = await accommodation_service.get_accommodation(
                    session=session, accommodation_id=accommodation_id
                )
                if accommodation:
                    if event.event_type == EventType.capacity_change:
                        accommodation.current_room_count = (
                            creation_event.initial_room_count
                        )
                    elif event.event_type == EventType.type_change:
                        accommodation.type = creation_event.initial_type
                    elif event.event_type == EventType.category_change:
                        accommodation.category_value = (
                            creation_event.initial_category_value
                        )
                        accommodation.category_system = (
                            creation_event.initial_category_system
                        )

    await session.delete(event)
    await session.commit()

    return True
