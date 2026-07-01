from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.accommodation.events.capacity_change import CapacityChange
from app.models.accommodation.events.category_change import CategoryChange
from app.models.accommodation.events.creation_event import CreationEvent
from app.models.accommodation.events.renovation import Renovation
from app.models.accommodation.events.type_change import TypeChange
from app.schemas.event import (
    BaseEventResponse,
    EventCreate,
    EventUpdate,
    CategoryChangeResponse,
    RenovationChangeResponse,
    TypeChangeResponse,
    CapacityChangeResponse,
    CreationEventResponse,
)

from app.core.dependencies import get_current_user, get_db
from app.models.core.user import User, UserRole
from app.models.accommodation.events.accommodation_event import EventType
from app.services import accommodation_service, event_service

router = APIRouter(prefix="/accommodations/{accommodation_id}/events")


@router.post("")
async def create_event(
    accommodation_id: int,
    data: EventCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can create events."
        )

    if data.event_type == "capacity_change":
        event = await event_service.create_capacity_change(
            session, accommodation_id, data
        )
        return CapacityChangeResponse.model_validate(event)

    elif data.event_type == "renovation":
        event = await event_service.create_renovation(session, accommodation_id, data)
        return RenovationChangeResponse.model_validate(event)

    elif data.event_type == "category_change":
        event = await event_service.create_category_change(
            session, accommodation_id, data
        )
        return CategoryChangeResponse.model_validate(event)

    elif data.event_type == "type_change":
        event = await event_service.create_type_change(session, accommodation_id, data)
        return TypeChangeResponse.model_validate(event)


@router.get("")
async def get_events(
    accommodation_id: int,
    event_type: EventType | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[
    CapacityChangeResponse
    | TypeChangeResponse
    | RenovationChangeResponse
    | CategoryChangeResponse
    | CreationEventResponse
]:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        # TODO: check entitlement when KAN-92 is implemented
        raise HTTPException(status_code=403, detail="Not authorized.")

    events = await event_service.get_events(
        session=session, accommodation_id=accommodation_id, event_type=event_type
    )

    response = []

    for event in events:
        print(type(event))
        if isinstance(event, CapacityChange):
            response.append(CapacityChangeResponse.model_validate(event))
        elif isinstance(event, CategoryChange):
            response.append(CategoryChangeResponse.model_validate(event))
        elif isinstance(event, Renovation):
            response.append(RenovationChangeResponse.model_validate(event))
        elif isinstance(event, TypeChange):
            response.append(TypeChangeResponse.model_validate(event))
        elif isinstance(event, CreationEvent):
            response.append(CreationEventResponse.model_validate(event))

    return response


@router.get("/{event_id}")
async def get_event(
    accommodation_id: int,
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> (
    CapacityChangeResponse
    | CategoryChangeResponse
    | RenovationChangeResponse
    | TypeChangeResponse
    | CreationEventResponse
):
    existing = await accommodation_service.get_accommodation(session, accommodation_id)

    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        # TODO: check entitlement when KAN-92 is implemented
        raise HTTPException(status_code=403, detail="Not authorized.")

    event = await event_service.get_event(
        session=session, accommodation_id=accommodation_id, event_id=event_id
    )
    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    if isinstance(event, CapacityChange):
        return CapacityChangeResponse.model_validate(event)
    elif isinstance(event, CategoryChange):
        return CategoryChangeResponse.model_validate(event)
    elif isinstance(event, Renovation):
        return RenovationChangeResponse.model_validate(event)
    elif isinstance(event, TypeChange):
        return TypeChangeResponse.model_validate(event)
    elif isinstance(event, CreationEvent):
        return CreationEventResponse.model_validate(event)
    else:
        raise HTTPException(status_code=400, detail="Unknown event type.")


@router.patch("/{event_id}")
async def patch_event(
    accommodation_id: int,
    event_id: int,
    data: EventUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can create events."
        )

    if data.event_type == "capacity_change":
        event = await event_service.update_capacity_change(session, event_id, data)
        return CapacityChangeResponse.model_validate(event)

    elif data.event_type == "renovation":
        event = await event_service.update_renovation(session, event_id, data)
        return RenovationChangeResponse.model_validate(event)

    elif data.event_type == "category_change":
        event = await event_service.update_category_change(session, event_id, data)
        return CategoryChangeResponse.model_validate(event)

    elif data.event_type == "type_change":
        event = await event_service.update_type_change(session, event_id, data)
        return TypeChangeResponse.model_validate(event)

    elif data.event_type == "created":
        event = await event_service.update_creation_event(session, event_id, data)
        return CreationEventResponse.model_validate(event)


@router.delete("/{event_id}")
async def delete_event(
    accommodation_id: int,
    event_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can delete events."
        )

    deleted = await event_service.delete_event(
        session=session, accommodation_id=accommodation_id, event_id=event_id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found.")

    return deleted
