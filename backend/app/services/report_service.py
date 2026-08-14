from typing import Sequence
from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.accommodation.accommodation import Accommodation
from app.models.accommodation.events.accommodation_event import EventType

from app.models.billing.entitlement import Entitlement
from app.models.markeplace.raw_product import RawProduct
from app.models.markeplace.aggregated_product import AggregatedProduct
from app.models.data.aggregation import Aggregation, AggregationParameters
from app.services import (
    accommodation_data_service,
    accommodation_service,
    event_service,
)
from app.models.accommodation.events.capacity_change import CapacityChange
from app.models.accommodation.events.category_change import CategoryChange
from app.models.accommodation.events.renovation import Renovation
from app.models.accommodation.events.type_change import TypeChange
from app.models.accommodation.events.creation_event import CreationEvent

from app.schemas.raw_report import (
    DistributionChannelReport,
    Financials,
    InventoryUnit,
    LocalMarketRisk,
    Overview,
    RevenueBreakdownReport,
    Valuation,
    YearlyPerformance,
    Operations,
    AssetStatus,
    HistoryAndRisk,
    RawReportResponse,
    MonthlyFinancials,
)

from app.schemas.event import (
    CapacityChangeResponse,
    CategoryChangeResponse,
    RenovationChangeResponse,
    TypeChangeResponse,
    CreationEventResponse,
)

from app.schemas.report_list import ReportListItem


# TODO: helper to get the rating score, sit down with the team
# to properly define, it should be put off until we're done with the pipeline
async def get_rating_score() -> int:
    """Get the rating score of the Accommodation"""
    score = 0
    return score


def compute_asset_class(adr: float) -> str:
    if adr >= 300:
        return "luxury"
    elif adr >= 200:
        return "upper_upscale"
    elif adr >= 140:
        return "upscale"
    elif adr >= 100:
        return "upper_midscale"
    elif adr >= 70:
        return "midscale"
    else:
        return "economy"


def event_to_response(ev):
    if isinstance(ev, Renovation):
        return RenovationChangeResponse.model_validate(ev)
    elif isinstance(ev, CapacityChange):
        return CapacityChangeResponse.model_validate(ev)
    elif isinstance(ev, CategoryChange):
        return CategoryChangeResponse.model_validate(ev)
    elif isinstance(ev, TypeChange):
        return TypeChangeResponse.model_validate(ev)
    elif isinstance(ev, CreationEvent):
        return CreationEventResponse.model_validate(ev)


async def get_reports(session: AsyncSession, org_id: int) -> Sequence[ReportListItem]:
    active_entitlements_query = (
        select(Entitlement)
        .where(Entitlement.org_id == org_id)
        .where(Entitlement.is_active)
    )
    active_entitlements_result = await session.execute(active_entitlements_query)
    active_entitlements = active_entitlements_result.scalars().all()

    report_items = []
    for entitlement in active_entitlements:
        if entitlement.raw_product_id:
            # query for the product if product does not exist just continue
            product_query = (
                select(RawProduct)
                .where(RawProduct.product_id == entitlement.raw_product_id)
                .where(RawProduct.is_active)
            )
            product_result = await session.execute(product_query)
            product = product_result.scalar_one_or_none()
            if not product:
                continue
            report_items.append(
                ReportListItem(
                    entitlement_id=entitlement.entitlement_id,
                    report_type="raw",
                    title=product.name,
                    period_type=product.granularity.value,
                    target_year=product.year,
                    target_period=None,
                    created_at=product.created_at,
                    status=product.status.value,
                )
            )
        elif entitlement.aggregated_product_id:
            product_query = select(AggregatedProduct).where(
                AggregatedProduct.product_id == entitlement.aggregated_product_id
            )
            product_result = await session.execute(product_query)
            product = product_result.scalar_one_or_none()
            if not product:
                continue

            aggregation_query = select(Aggregation).where(
                Aggregation.aggregation_id == product.aggregation_id
            )
            aggregation_result = await session.execute(aggregation_query)
            aggregation = aggregation_result.scalar_one_or_none()

            params = (
                AggregationParameters(**aggregation.parameters)
                if aggregation
                else AggregationParameters()
            )

            report_items.append(
                ReportListItem(
                    entitlement_id=entitlement.entitlement_id,
                    report_type="aggregated",
                    title=product.name,
                    period_type="Yearly",  # TODO: Aggregation has no granularity field yet
                    target_year=params.year_to,
                    target_period=None,
                    created_at=product.created_at,
                    status=product.status.value,
                )
            )

    return report_items


async def get_raw_report(
    session: AsyncSession, entitlement_id: int, org_id: int
) -> RawReportResponse:
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
        include_historical=True,
    )

    inventory_units = [
        InventoryUnit(unit_type=rt.level, count=rt.count) for rt in room_types
    ]

    overview = Overview(
        total_units=accommodation.current_room_count,
        property_type=accommodation.type.value.capitalize(),
        # TODO: Compute using the adr from accommodation data when pipeline is implemented
        asset_class=None,
        ownership_structure=accommodation.ownership_structure,
        rating_type=accommodation.category_system,
        rating_value=str(accommodation.category_value),
        # TODO: Implement the formula, and a helper to calculate it uses PIPELINE
        grade=None,  # TODO: pipeline — formula pending, see get_rating_score()
        year=accommodation.building_year,
        inventory_mix=inventory_units,
    )

    # TODO: pending pipeline connection — revenue_breakdown snapshot for raw_product.year
    # revenue_breakdown = [RevenueBreakdownReport() for rb in revenue_breakdowns]

    # TODO: pending pipeline connection
    # yearly_performances = [YearlyPerformance() for yp in ]

    # TODO: pending pipeline connection
    # monthly_financials = [MonthlyFinancials() for mf in ]

    # TODO: pending pipeline connection
    # forecast_next_year =

    # TODO: pending pipeline connection
    # day_of_week_occupancy= ""

    # TODO: peding data form pipeline connection
    # financials = Financials(total_revenue=,
    #                         revpar=,
    #                         adr=,
    #                         gop_margin=,
    #                         revenue_breakdown=,
    #                         historical_performance=,
    #                         forecast_next_year=,
    #                         monthly_revenue=
    #                         )

    # Comission cost may be a sensitive data  it should be None
    d_channels_reports = [
        DistributionChannelReport(
            channel_name=dc.channel_name,
            booking_percentage=dc.booking_percentage,
            commission_cost=dc.commission_cost,
        )
        for dc in distribution_channels
    ]

    # operations = Operations(day_of_week_occupancy=day_of_week_occupancy,
    #            distribution_channels=d_channels_reports)

    # TODO: pipeline depending
    # market_positioning = []

    # TODO:  pipeline depending
    # valuation = Valuation()

    asset_events = [event_to_response(ev) for ev in events]

    if not accommodation.building_year:
        raise HTTPException(422, detail="Building year accommodation is missing.")
    age_years = date.today().year - accommodation.building_year
    last_renovations = await event_service.get_events(
        session=session,
        accommodation_id=accommodation.id,
        event_type=EventType.renovation,
        order_by_date_desc=True,
    )

    if last_renovations:
        last_renovation_year = last_renovations[0].effective_date.year
    else:
        last_renovation_year = None

    accommodation_certifications = (
        await accommodation_service.get_accommodation_certifications(
            session=session, accommodation_id=accommodation.id
        )
    )

    asset_status = AssetStatus(
        last_renovation_year=last_renovation_year,
        building_age_years=age_years,
        next_estimated_renovation=None,
        certifications=[
            ac.certification_type.value for ac in accommodation_certifications
        ],
    )

    # TODO: pipeline depending
    # local_market = LocalMarketRisk()

    history_and_risk = HistoryAndRisk(
        historical_events=asset_events, asset_status=asset_status, local_market=None
    )

    # TODO: set up the satisfaction stuff but honestly I donw think it s gonna make it for the MVP

    raw_report_response = RawReportResponse(
        property_name=accommodation.name,
        # TODO: format this now is a dictionary
        location=f"{accommodation.location['city']}, {accommodation.location['nuts3']}",
        overview=overview,
        # financials=financials,
        # operations=operations,
        # market_positioning=market_positioning,
        # valuation=valuation,
        history_and_risk=history_and_risk,
        satisfaction=None,
    )

    return raw_report_response


async def get_aggregated_report(
    session: AsyncSession, entitlement_id: int, org_id: int
):
    # Construct AggregatedReportResponse
    pass
