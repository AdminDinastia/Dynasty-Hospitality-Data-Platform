from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
import stripe

from app.models.accommodation.accommodation import Accommodation
from app.models.billing.entitlement import Entitlement, EntitlementType
from app.models.billing.points_ledger import PointsLedger, PointsReason
from app.models.core.organization import Organization
from app.models.markeplace.aggregated_product import AggregatedProduct
from app.models.markeplace.raw_product import RawProduct

from app.models.markeplace.product_status import ProductStatus
from app.models.accommodation.data_sharing_consent import DataSharingConsent
from app.models.billing.revenue_distribution import (
    RevenueDistribution,
    RevenueDistributionStatus,
)
from app.models.data.aggregation import Aggregation
from app.schemas.product import (
    AggregatedProductFilters,
    RawProductFilters,
)


async def get_aggregated_products(
    session: AsyncSession, filters: AggregatedProductFilters
) -> Sequence[AggregatedProduct]:
    query = (
        select(AggregatedProduct)
        .join(
            Aggregation, AggregatedProduct.aggregation_id == Aggregation.aggregation_id
        )
        .where(AggregatedProduct.is_active)
    )

    if filters.nuts_code:
        level = len(filters.nuts_code)
        key = {3: "nuts1", 4: "nuts2", 5: "nuts3"}[level]
        query = query.where(Aggregation.parameters[key] == filters.nuts_code)

    elif filters.country:
        query = query.where(
            Aggregation.parameters["country"].as_text == filters.country
        )
    if filters.city:
        query = query.where(Aggregation.parameters["city"].as_text == filters.city)

    if filters.category_system:
        query = query.where(
            Aggregation.parameters["category_system"].as_text == filters.category_system
        )

    if filters.min_category:
        query = query.where(
            Aggregation.parameters["min_category"] >= filters.min_category
        )
    if filters.max_category:
        query = query.where(
            Aggregation.parameters["max_category"] <= filters.max_category
        )
    if filters.type:
        query = query.where(Aggregation.parameters["type"] == filters.type)

    if filters.year_from:
        query = query.where(Aggregation.parameters["year_from"] >= filters.year_from)
    if filters.year_to:
        query = query.where(Aggregation.parameters["year_to"] <= filters.year_to)

    if filters.status:
        query = query.where(AggregatedProduct.status == filters.status)

    result = await session.execute(query)

    return result.scalars().all()


async def get_aggregated_product(
    product_id: int,
    session: AsyncSession,
) -> AggregatedProduct | None:
    query = (
        select(AggregatedProduct)
        .where(AggregatedProduct.product_id == product_id)
        .where(AggregatedProduct.is_active)
    )

    result = await session.execute(query)
    agg_product = result.scalar_one_or_none()

    if not agg_product:
        return None
    if agg_product.status != ProductStatus.active:
        raise HTTPException(
            status_code=409, detail="This product's data is not ready yet."
        )

    return agg_product


async def get_raw_products(
    session: AsyncSession, filters: RawProductFilters
) -> Sequence[RawProduct]:
    query = select(RawProduct).where(RawProduct.is_active)

    if filters.accommodation_id:
        query = query.where(RawProduct.accommodation_id == filters.accommodation_id)

    if filters.year:
        query = query.where(RawProduct.year == filters.year)

    if filters.status:
        query = query.where(RawProduct.status == filters.status)

    if filters.purchasable:
        query = (
            query.join(
                DataSharingConsent,
                RawProduct.accommodation_id == DataSharingConsent.accommodation_id,
            )
            .where(DataSharingConsent.allow_raw_sharing)
            .where(RawProduct.status == ProductStatus.active)
        )

    if filters.granularity:
        query = query.where(RawProduct.granularity == filters.granularity)

    result = await session.execute(query)
    raw_product = result.scalars().all()

    return raw_product


async def get_raw_product(
    product_id: int,
    session: AsyncSession,
) -> RawProduct | None:
    query = (
        select(RawProduct)
        .where(RawProduct.product_id == product_id)
        .where(RawProduct.is_active)
    )
    result = await session.execute(query)
    raw_pr = result.scalar_one_or_none()
    if not raw_pr:
        return None
    if raw_pr.status != ProductStatus.active:
        raise HTTPException(
            status_code=409, detail="This product's data is not ready yet."
        )
    return raw_pr


async def purchase_aggregated_product(
    org_id: int,
    product_id: int,
    session: AsyncSession,
) -> Entitlement:
    query = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(query)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    query = select(AggregatedProduct).where(AggregatedProduct.product_id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product was not found.")

    if not (org.points_balance >= product.price_points):
        raise HTTPException(status_code=403, detail="Insufficient points.")

    if product.status != ProductStatus.active:
        raise HTTPException(
            status_code=409, detail="This product is not ready to purchase yet."
        )

    query = (
        select(Entitlement)
        .where(Entitlement.org_id == org_id)
        .where(Entitlement.aggregated_product_id == product_id)
    )
    result = await session.execute(query)
    previous_entitl = result.scalar_one_or_none()

    if previous_entitl:
        raise HTTPException(409, detail="Product is already owned by the user.")

    if not product.is_active:
        raise HTTPException(status_code=403, detail="Product is not active.")

    org.points_balance -= product.price_points

    new_points_ledger = PointsLedger(
        org_id=org_id,
        points=-product.price_points,
        reason=PointsReason.product_access,
        reference_id=product.product_id,
        reference_type="aggregated_product",
    )

    new_entitl = Entitlement(
        aggregated_product_id=product_id,
        entitlement_type=EntitlementType.points,
        org_id=org_id,
    )
    session.add(new_points_ledger)
    session.add(new_entitl)
    await session.commit()
    await session.refresh(new_entitl)

    return new_entitl


async def purchase_raw_product(
    org_id: int,
    product_id: int,
    session: AsyncSession,
) -> Entitlement:
    query = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(query)
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    query = select(RawProduct).where(RawProduct.product_id == product_id)
    result = await session.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product was not found.")

    if not (org.points_balance >= product.price_points):
        raise HTTPException(status_code=403, detail="Insufficient points.")

    if product.status != ProductStatus.active:
        raise HTTPException(
            status_code=409, detail="This product is not ready to purchase yet."
        )

    query = (
        select(Entitlement)
        .where(Entitlement.org_id == org_id)
        .where(Entitlement.raw_product_id == product_id)
    )
    result = await session.execute(query)
    previous_entitl = result.scalar_one_or_none()

    if previous_entitl:
        raise HTTPException(409, detail="Product is already owned by the user.")

    if not product.is_active:
        raise HTTPException(status_code=403, detail="Product is not active.")

    org.points_balance -= product.price_points

    new_points_ledger = PointsLedger(
        org_id=org_id,
        points=-product.price_points,
        reason=PointsReason.product_access,
        reference_id=product.product_id,
        reference_type="raw_product",
    )

    new_entitl = Entitlement(
        raw_product_id=product_id,
        entitlement_type=EntitlementType.points,
        org_id=org_id,
    )

    session.add(new_points_ledger)
    session.add(new_entitl)
    await session.commit()

    # Obtain DataSharingConsent for accommodation
    accommodation_query = select(Accommodation).where(
        Accommodation.id == product.accommodation_id
    )
    accommodation_result = await session.execute(accommodation_query)
    accommodation = accommodation_result.scalar_one_or_none()

    provider_org_query = select(Organization).where(
        Organization.org_id == accommodation.org_id
    )
    provider_org_result = await session.execute(provider_org_query)
    provider_org = provider_org_result.scalar_one_or_none()

    dsc_query = select(DataSharingConsent).where(
        DataSharingConsent.accommodation_id == product.accommodation_id
    )
    dsc_result = await session.execute(dsc_query)
    data_sharing_consent = dsc_result.scalar_one_or_none()

    if not data_sharing_consent:
        # No consent configured
        await session.refresh(new_entitl)
        return new_entitl

    provider_amount = (
        product.price_points * data_sharing_consent.revenue_share_pct
    ) / 100

    stripe_transfer_id = None
    if provider_org and provider_org.stripe_account_id:
        transfer = await stripe.Transfer.create_async(
            amount=int(provider_amount * 100),
            currency="eur",
            destination=provider_org.stripe_account_id,
        )
        stripe_transfer_id = transfer.id

    new_rev_distribution = RevenueDistribution(
        raw_product_id=product.product_id,
        buyer_org_id=org_id,
        org_id=provider_org.org_id,
        accommodation_id=product.accommodation_id,
        amount=int(provider_amount),
        revenue_share_pct=data_sharing_consent.revenue_share_pct,
        stripe_transfer_id=stripe_transfer_id,
        status=RevenueDistributionStatus.paid
        if stripe_transfer_id
        else RevenueDistributionStatus.pending,
    )

    session.add(new_rev_distribution)
    await session.commit()

    await session.refresh(new_entitl)

    return new_entitl
