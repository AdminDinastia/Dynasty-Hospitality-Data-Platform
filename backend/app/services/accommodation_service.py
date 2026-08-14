from typing import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accommodation.accommodation import Accommodation
from app.models.accommodation.accommodation_details import AccommodationDetails
from app.models.accommodation.room_types import RoomType
from app.models.accommodation.distribution_channels import DistributionChannel
from app.models.accommodation.revenue_breakdown import RevenueBreakdown
from app.services import data_sharing_service
from app.models.accommodation.accommodation_theme import AccommodationTheme
from app.models.accommodation.accommodation_certification import (
    AccommodationCertification,
)
from app.schemas.accommodation_extended import (
    AccommodationThemeCreate,
    AccommodationCertificationCreate,
)

from app.schemas.accommodation import AccommodationCreate, AccommodationUpdate
from app.schemas.accommodation_extended import (
    DistributionChannelUpdate,
    RoomTypeCreate,
    DistributionChannelCreate,
    AccommodationDetailsCreate,
    AccommodationDetailsUpdate,
    RevenueBreakdownCreate,
)
from app.services import event_service


async def create_accommodation(
    session: AsyncSession,
    data: AccommodationCreate,
    org_id: int,
) -> Accommodation:
    location_dict = data.location.model_dump()
    location_dict["nuts1"] = data.location.nuts3[:3]
    location_dict["nuts2"] = data.location.nuts3[:4]

    new_accommodation = Accommodation(
        name=data.name,
        org_id=org_id,
        location=location_dict,
        type=data.type,
        category_system=data.category_system,
        category_value=data.category_value,
        current_room_count=data.current_room_count,
        building_year=data.building_year,
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
        .where(Accommodation.is_active)
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
        .where(Accommodation.is_active)
    )
    result = await session.execute(query)
    accommodation = result.scalar_one_or_none()

    return accommodation


async def update_accommodation(
    session: AsyncSession, accommodation_id: int, data: AccommodationUpdate
) -> Accommodation | None:
    query = select(Accommodation).where(Accommodation.id == accommodation_id)
    result = await session.execute(query)
    accommodation = result.scalar_one_or_none()

    if not accommodation:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "location" in update_data and update_data["location"]:
        loc = update_data["location"]
        loc["nuts1"] = loc["nuts3"][:3]
        loc["nuts2"] = loc["nuts3"][:4]
        update_data["location"] = loc

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

    accommodation.is_active = False
    accommodation.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return True


async def create_room_type(
    session: AsyncSession,
    accommodation_id: int,
    data: RoomTypeCreate,
) -> RoomType:
    new_room_type = RoomType(
        accommodation_id=accommodation_id,
        category=data.category,
        level=data.level,
        custom_name=data.custom_name,
        count=data.count,
    )
    session.add(new_room_type)
    await session.commit()

    return new_room_type


async def get_room_type(session: AsyncSession, room_type_id: int) -> RoomType | None:
    room_types_query = select(RoomType).where(RoomType.room_type_id == room_type_id)
    room_types_result = await session.execute(room_types_query)
    room_type = room_types_result.scalar_one_or_none()

    return room_type


async def get_room_types(
    session: AsyncSession, accommodation_id: int
) -> Sequence[RoomType]:
    room_types_query = select(RoomType).where(
        RoomType.accommodation_id == accommodation_id
    )
    room_types_result = await session.execute(room_types_query)
    room_types = room_types_result.scalars().all()

    return room_types


async def delete_room_type(session: AsyncSession, room_type_id: int) -> bool:
    room_type_query = select(RoomType).where(RoomType.room_type_id == room_type_id)
    room_type_result = await session.execute(room_type_query)
    room_type = room_type_result.scalar_one_or_none()

    if not room_type:
        return False

    await session.delete(room_type)
    await session.commit()
    return True


async def create_distribution_channel(
    session: AsyncSession, accommodation_id: int, data: DistributionChannelCreate
) -> DistributionChannel:
    new_distribution_channel = DistributionChannel(
        accommodation_id=accommodation_id,
        year=data.year,
        channel_name=data.channel_name,
        booking_percentage=data.booking_percentage,
        commission_cost=data.commission_cost,
    )
    session.add(new_distribution_channel)
    await session.commit()
    return new_distribution_channel


async def get_distribution_channels(
    session: AsyncSession,
    accommodation_id: int,
    year: int | None = None,
    include_historical: bool = False,
) -> Sequence[DistributionChannel]:
    dc_query = select(DistributionChannel).where(
        DistributionChannel.accommodation_id == accommodation_id
    )
    if year:
        if include_historical:
            dc_query = dc_query.where(DistributionChannel.year <= year)
        else:
            dc_query = dc_query.where(DistributionChannel.year == year)
    dc_result = await session.execute(dc_query)
    distribution_channels = dc_result.scalars().all()

    return distribution_channels


async def get_distribution_channel(
    session: AsyncSession, channel_id: int
) -> DistributionChannel | None:
    dc_query = select(DistributionChannel).where(
        DistributionChannel.channel_id == channel_id
    )
    dc_result = await session.execute(dc_query)
    distribution_channel = dc_result.scalar_one_or_none()
    return distribution_channel


async def update_distribution_channels(
    session: AsyncSession, channel_id: int, data: DistributionChannelUpdate
) -> DistributionChannel | None:
    dc_query = select(DistributionChannel).where(
        DistributionChannel.channel_id == channel_id
    )
    dc_result = await session.execute(dc_query)
    distribution_channel = dc_result.scalar_one_or_none()

    if not distribution_channel:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(distribution_channel, field, value)

    await session.commit()
    return distribution_channel


async def delete_distribution_channel(session: AsyncSession, channel_id: int) -> bool:
    dc_query = select(DistributionChannel).where(
        DistributionChannel.channel_id == channel_id
    )
    dc_result = await session.execute(dc_query)
    dc = dc_result.scalar_one_or_none()

    if not dc:
        return False

    await session.delete(dc)
    await session.commit()
    return True


async def create_revenue_breakdowns(
    session: AsyncSession, accommodation_id: int, data: RevenueBreakdownCreate
) -> RevenueBreakdown:
    new_revenue_breakdown = RevenueBreakdown(
        accommodation_id=accommodation_id,
        year=data.year,
        department=data.department,
        revenue=data.revenue,
    )
    session.add(new_revenue_breakdown)
    await session.commit()
    return new_revenue_breakdown


async def get_revenue_breakdowns(
    session: AsyncSession,
    accommodation_id: int,
    year: int | None = None,
    include_historical: bool = False,
) -> Sequence[RevenueBreakdown]:
    rb_query = select(RevenueBreakdown).where(
        RevenueBreakdown.accommodation_id == accommodation_id
    )
    if year:
        rb_query = rb_query.where(RevenueBreakdown.year == year)

    if year:
        if include_historical:
            rb_query = rb_query.where(RevenueBreakdown.year <= year)
        else:
            rb_query = rb_query.where(RevenueBreakdown.year == year)

    rb_result = await session.execute(rb_query)
    revenue_breakdowns = rb_result.scalars().all()

    return revenue_breakdowns


async def get_revenue_breakdown(
    session: AsyncSession, breakdown_id: int
) -> RevenueBreakdown | None:
    rb_query = select(RevenueBreakdown).where(
        RevenueBreakdown.breakdown_id == breakdown_id
    )
    rb_result = await session.execute(rb_query)
    revenue_breakdown = rb_result.scalar_one_or_none()

    return revenue_breakdown


async def delete_revenue_breakdowns(session: AsyncSession, breakdown_id: int) -> bool:
    rb_query = select(RevenueBreakdown).where(
        RevenueBreakdown.breakdown_id == breakdown_id
    )
    rb_result = await session.execute(rb_query)
    revenue_breakdown = rb_result.scalar_one_or_none()

    if not revenue_breakdown:
        return False

    await session.delete(revenue_breakdown)
    await session.commit()
    return True


async def create_accommodation_details(
    session: AsyncSession, accommodation_id: int, data: AccommodationDetailsCreate
) -> AccommodationDetails:
    new_accommodation_details = AccommodationDetails(
        accommodation_id=accommodation_id,
        year=data.year,
        lead_time_days=data.lead_time_days,
        length_of_stay=data.length_of_stay,
        cpor=data.cpor,
        employee_count=data.employee_count,
    )
    session.add(new_accommodation_details)
    await session.commit()
    return new_accommodation_details


async def get_accommodation_details(
    session: AsyncSession,
    accommodation_id: int,
    year: int | None = None,
    include_historical: bool = False,
) -> Sequence[AccommodationDetails]:
    accommodation_details_query = select(AccommodationDetails).where(
        AccommodationDetails.accommodation_id == accommodation_id
    )
    if year:
        if include_historical:
            accommodation_details_query = accommodation_details_query.where(
                AccommodationDetails.year <= year
            )
        else:
            accommodation_details_query = accommodation_details_query.where(
                AccommodationDetails.year == year
            )

    accommodation_details_result = await session.execute(accommodation_details_query)
    accommodation_details = accommodation_details_result.scalars().all()

    return accommodation_details


async def get_accommodation_detail(
    session: AsyncSession, detail_id: int
) -> AccommodationDetails | None:
    accommodation_details_query = select(AccommodationDetails).where(
        AccommodationDetails.detail_id == detail_id
    )

    accommodation_details_result = await session.execute(accommodation_details_query)
    accommodation_detail = accommodation_details_result.scalar_one_or_none()

    return accommodation_detail


async def update_accommodation_details(
    session: AsyncSession, detail_id: int, data: AccommodationDetailsUpdate
) -> AccommodationDetails | None:
    accommodation_details_query = select(AccommodationDetails).where(
        AccommodationDetails.detail_id == detail_id
    )
    accommodation_details_result = await session.execute(accommodation_details_query)
    accommodation_details = accommodation_details_result.scalar_one_or_none()

    if not accommodation_details:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(accommodation_details, field, value)

    await session.commit()
    return accommodation_details


async def create_accommodation_theme(
    session: AsyncSession, accommodation_id: int, data: AccommodationThemeCreate
) -> AccommodationTheme:
    new_theme = AccommodationTheme(
        accommodation_id=accommodation_id,
        theme_type=data.theme_type,
    )
    session.add(new_theme)
    await session.commit()
    return new_theme


async def get_accommodation_themes(
    session: AsyncSession, accommodation_id: int
) -> Sequence[AccommodationTheme]:
    query = select(AccommodationTheme).where(
        AccommodationTheme.accommodation_id == accommodation_id
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_accommodation_theme(
    session: AsyncSession, theme_id: int
) -> AccommodationTheme | None:
    query = select(AccommodationTheme).where(AccommodationTheme.theme_id == theme_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def delete_accommodation_theme(session: AsyncSession, theme_id: int) -> bool:
    theme = await get_accommodation_theme(session, theme_id)
    if not theme:
        return False
    await session.delete(theme)
    await session.commit()
    return True


async def create_accommodation_certification(
    session: AsyncSession, accommodation_id: int, data: AccommodationCertificationCreate
) -> AccommodationCertification:
    new_certification = AccommodationCertification(
        accommodation_id=accommodation_id,
        certification_type=data.certification_type,
        custom_name=data.custom_name,
        obtained_year=data.obtained_year,
    )
    session.add(new_certification)
    await session.commit()
    return new_certification


async def get_accommodation_certifications(
    session: AsyncSession, accommodation_id: int
) -> Sequence[AccommodationCertification]:
    query = select(AccommodationCertification).where(
        AccommodationCertification.accommodation_id == accommodation_id
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_accommodation_certification(
    session: AsyncSession, certification_id: int
) -> AccommodationCertification | None:
    query = select(AccommodationCertification).where(
        AccommodationCertification.certification_id == certification_id
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def delete_accommodation_certification(
    session: AsyncSession, certification_id: int
) -> bool:
    certification = await get_accommodation_certification(session, certification_id)
    if not certification:
        return False
    await session.delete(certification)
    await session.commit()
    return True
