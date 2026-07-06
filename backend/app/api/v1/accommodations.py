from typing import List

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.accommodation.events.accommodation_event import EventType
from app.schemas.accommodation import (
    AccommodationCreate,
    AccommodationResponse,
    AccommodationUpdate,
)


from app.core.dependencies import get_current_user, get_db
from app.models.core.user import User, UserRole
from app.schemas.data_sharing import DataSharingUpdate, DataSharingConsentResponse
from app.services import accommodation_service, data_sharing_service
from app.models.accommodation.data_sharing_consent import DataSharingConsent


# Import the functions here from the services so the business logic is not exposed
router = APIRouter(prefix="/accommodations")


@router.post("")
async def create_accommodation(
    data: AccommodationCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AccommodationResponse:
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can create accommodations."
        )

    accommodation = await accommodation_service.create_accommodation(
        session, data, user.org_id
    )
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if accommodation.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    response = AccommodationResponse.model_validate(accommodation)
    response.tags = [tag.name for tag in accommodation.tags]
    return response


@router.get("")
async def get_accommodations(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[AccommodationResponse]:
    accommodations = await accommodation_service.get_accommodations(
        session, user.org_id
    )
    return [
        AccommodationResponse(
            name=a.name,
            city=a.city,
            country=a.country,
            type=a.type,
            category_system=a.category_system,
            category_value=a.category_value,
            current_room_count=a.current_room_count,
            id=a.id,
            org_id=a.org_id,
            created_at=a.created_at,
            updated_at=a.updated_at,
            tags=[tag.name for tag in a.tags],
        )
        for a in accommodations
    ]


@router.get("/{accommodation_id}")
async def get_accommodation(
    accommodation_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AccommodationResponse:
    accommodation = await accommodation_service.get_accommodation(
        session, accommodation_id
    )
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    return AccommodationResponse(
        name=accommodation.name,
        city=accommodation.city,
        country=accommodation.country,
        type=accommodation.type,
        category_system=accommodation.category_system,
        category_value=accommodation.category_value,
        current_room_count=accommodation.current_room_count,
        id=accommodation.id,
        org_id=accommodation.org_id,
        created_at=accommodation.created_at,
        updated_at=accommodation.updated_at,
        tags=[tag.name for tag in accommodation.tags],
    )


@router.patch("/{accommodation_id}")
async def patch_accommodation(
    accommodation_id: int,
    data: AccommodationUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AccommodationResponse:
    # check the user is in the organization and the owner
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")

    if existing.org_id != user.org_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this accommodation."
        )
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can update accommodations."
        )

    accommodation = await accommodation_service.update_accommodation(
        session, accommodation_id, data
    )

    return AccommodationResponse(
        name=accommodation.name,
        city=accommodation.city,
        country=accommodation.country,
        type=accommodation.type,
        category_system=accommodation.category_system,
        category_value=accommodation.category_value,
        current_room_count=accommodation.current_room_count,
        id=accommodation.id,
        org_id=accommodation.org_id,
        created_at=accommodation.created_at,
        updated_at=accommodation.updated_at,
        tags=[tag.name for tag in accommodation.tags],
    )


@router.patch("/{accommodation_id}/data-sharing")
async def patch_accommodation_data_sharing_consent(
    accommodation_id: int,
    data: DataSharingUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DataSharingConsentResponse:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(status_code=403, detail="Only org admins can update this.")

    updated_consent = await data_sharing_service.update_consent(
        session, accommodation_id, data
    )
    if not updated_consent:
        raise HTTPException(status_code=404, detail="Data Sharing consent not found.")

    return DataSharingConsentResponse(
        consent_id=updated_consent.consent_id,
        accommodation_id=updated_consent.accommodation_id,
        allow_aggregated=updated_consent.allow_aggregated,
        allow_raw_sharing=updated_consent.allow_raw_sharing,
        revenue_share_pct=updated_consent.revenue_share_pct,
        terms_version=updated_consent.terms_version,
        consent_given_at=updated_consent.consent_given_at,
        revoked_at=updated_consent.revoked_at,
    )


@router.delete("/{accommodation_id}")
async def delete_accommodation(
    accommodation_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> bool:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can delete accommodations."
        )

    deleted = await accommodation_service.delete_accommodation(
        session, accommodation_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    return deleted
