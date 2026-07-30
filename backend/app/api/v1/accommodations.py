from typing import List

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.accommodation import (
    AccommodationCreate,
    AccommodationResponse,
    AccommodationUpdate,
)
from app.schemas.accommodation_extended import (
    AccommodationDetailsResponse,
    AccommodationDetailsUpdate,
    AccommodationDetailsCreate,
    DistributionChannelCreate,
    RoomTypeCreate,
    RoomTypeResponse,
    DistributionChannelUpdate,
    DistributionChannelResponse,
    RevenueBreakdownCreate,
    RevenueBreakdownResponse,
)


from app.core.dependencies import get_current_user, get_db
from app.models.core.user import User, UserRole
from app.schemas.data_sharing import DataSharingUpdate, DataSharingConsentResponse
from app.services import accommodation_service, data_sharing_service


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
            location=a.location,
            type=a.type,
            category_system=a.category_system,
            category_value=a.category_value,
            current_room_count=a.current_room_count,
            id=a.id,
            org_id=a.org_id,
            created_at=a.created_at,
            updated_at=a.updated_at,
            building_year=a.building_year,
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
        location=accommodation.location,
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
        location=accommodation.location,
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


@router.post("/{accommodation_id}/room-types")
async def create_room_type(
    accommodation_id: int,
    data: RoomTypeCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RoomTypeResponse:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can add room types."
        )
    total_rooms = existing.current_room_count

    percentage = (data.count / total_rooms * 100) if total_rooms else None

    room_type = await accommodation_service.create_room_type(
        session=session, accommodation_id=accommodation_id, data=data
    )
    return RoomTypeResponse(
        room_type_id=room_type.room_type_id,
        category=room_type.category,
        level=room_type.level,
        custom_name=room_type.custom_name,
        count=room_type.count,
        percentage=percentage,
    )


@router.get("/{accommodation_id}/room-types")
async def get_room_types(
    accommodation_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[RoomTypeResponse]:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    total_rooms = existing.current_room_count
    room_types = await accommodation_service.get_room_types(
        session=session,
        accommodation_id=accommodation_id,
    )
    return [
        RoomTypeResponse(
            room_type_id=rt.room_type_id,
            category=rt.category,
            level=rt.level,
            custom_name=rt.custom_name,
            count=rt.count,
            percentage=(rt.count / total_rooms * 100) if total_rooms else None,
        )
        for rt in room_types
    ]


@router.delete("/room-types/{room_type_id}")
async def delete_room_type(
    room_type_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> bool:
    room_type = await accommodation_service.get_room_type(
        session=session, room_type_id=room_type_id
    )
    if not room_type:
        raise HTTPException(status_code=404, detail="Room type not found.")
    existing = await accommodation_service.get_accommodation(
        session, room_type.accommodation_id
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can delete room types."
        )
    response = await accommodation_service.delete_room_type(
        session=session, room_type_id=room_type_id
    )
    return response


@router.post("/{accommodation_id}/distribution-channels")
async def create_distribution_channel(
    accommodation_id: int,
    data: DistributionChannelCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DistributionChannelResponse:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can add distribution channels"
        )
    distribution_channel = await accommodation_service.create_distribution_channel(
        session=session, accommodation_id=accommodation_id, data=data
    )
    return DistributionChannelResponse.model_validate(distribution_channel)


@router.get("/{accommodation_id}/distribution-channels")
async def get_distribution_channels(
    accommodation_id: int,
    year: int | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[DistributionChannelResponse]:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    distribution_channels = await accommodation_service.get_distribution_channels(
        session=session, accommodation_id=accommodation_id, year=year
    )
    return [
        DistributionChannelResponse.model_validate(dc) for dc in distribution_channels
    ]


@router.patch("/distribution-channels/{channel_id}")
async def update_distribution_channel(
    channel_id: int,
    data: DistributionChannelUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DistributionChannelResponse:
    dc = await accommodation_service.get_distribution_channel(
        session=session, channel_id=channel_id
    )
    if not dc:
        raise HTTPException(status_code=404, detail="Distribution Channel not found.")

    existing = await accommodation_service.get_accommodation(
        session, dc.accommodation_id
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can update distribution channels"
        )
    distribution_channel = await accommodation_service.update_distribution_channels(
        session=session, channel_id=channel_id, data=data
    )
    return DistributionChannelResponse.model_validate(distribution_channel)


@router.delete("/distribution-channels/{channel_id}")
async def delete_distribution_channel(
    channel_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> bool:
    dc = await accommodation_service.get_distribution_channel(
        session=session, channel_id=channel_id
    )
    if not dc:
        raise HTTPException(status_code=404, detail="Distribution Channel not found.")

    existing = await accommodation_service.get_accommodation(
        session, dc.accommodation_id
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can delete accommodations."
        )

    deleted = await accommodation_service.delete_distribution_channel(
        session=session, channel_id=channel_id
    )
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Distribution Channel was not found."
        )
    return deleted


@router.post("/{accommodation_id}/revenue-breakdown")
async def create_revenue_breakdowns(
    accommodation_id: int,
    data: RevenueBreakdownCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RevenueBreakdownResponse:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can add room types."
        )
    revenue_breakdown = await accommodation_service.create_revenue_breakdowns(
        session=session, accommodation_id=accommodation_id, data=data
    )

    return RevenueBreakdownResponse(
        breakdown_id=revenue_breakdown.breakdown_id,
        year=revenue_breakdown.year,
        department=revenue_breakdown.department,
        revenue=revenue_breakdown.revenue,
        percentage=None,
    )


@router.get("/{accommodation_id}/revenue-breakdown")
async def get_revenue_breakdowns(
    accommodation_id: int,
    year: int | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[RevenueBreakdownResponse]:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    revenue_breakdowns = await accommodation_service.get_revenue_breakdowns(
        session=session, accommodation_id=accommodation_id, year=year
    )
    total_revenue = sum(rb.revenue for rb in revenue_breakdowns)
    return [
        RevenueBreakdownResponse(
            breakdown_id=rb.breakdown_id,
            year=rb.year,
            department=rb.department,
            revenue=rb.revenue,
            percentage=(rb.revenue / total_revenue * 100) if total_revenue else None,
        )
        for rb in revenue_breakdowns
    ]


@router.delete("/revenue-breakdown/{breakdown_id}")
async def delete_revenue_breakdown(
    breakdown_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> bool:
    rb = await accommodation_service.get_revenue_breakdown(
        session=session, breakdown_id=breakdown_id
    )

    if not rb:
        raise HTTPException(status_code=404, detail="Revenue Breakdown not found.")

    existing = await accommodation_service.get_accommodation(
        session, rb.accommodation_id
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can remove Revenue Breakdown."
        )

    response = await accommodation_service.delete_revenue_breakdowns(
        session=session, breakdown_id=breakdown_id
    )
    return response


@router.post("/{accommodation_id}/details")
async def create_accommodation_details(
    accommodation_id: int,
    data: AccommodationDetailsCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AccommodationDetailsResponse:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    accommodation_details = await accommodation_service.create_accommodation_details(
        session=session, accommodation_id=accommodation_id, data=data
    )

    return AccommodationDetailsResponse.model_validate(accommodation_details)


@router.get("/{accommodation_id}/details")
async def get_accommodation_details(
    accommodation_id: int,
    year: int | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[AccommodationDetailsResponse]:
    existing = await accommodation_service.get_accommodation(session, accommodation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    accommodation_details = await accommodation_service.get_accommodation_details(
        session=session, accommodation_id=accommodation_id, year=year
    )
    return [
        AccommodationDetailsResponse.model_validate(ad) for ad in accommodation_details
    ]


@router.patch("/details/{detail_id}")
async def update_accommodation_details(
    detail_id: int,
    data: AccommodationDetailsUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AccommodationDetailsResponse | None:
    ad = await accommodation_service.get_accommodation_detail(
        session=session, detail_id=detail_id
    )
    if not ad:
        raise HTTPException(status_code=404, detail="Accommodation Details not found.")

    existing = await accommodation_service.get_accommodation(
        session, ad.accommodation_id
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if existing.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    accommodation_details = await accommodation_service.update_accommodation_details(
        session=session, detail_id=detail_id, data=data
    )
    return AccommodationDetailsResponse.model_validate(accommodation_details)
