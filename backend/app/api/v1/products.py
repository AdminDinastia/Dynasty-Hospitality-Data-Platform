from typing import Annotated, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.core.user import User
from app.core.dependencies import get_current_user, get_db
from app.services import product_service
from app.schemas.product import (
    AggregatedProductFilters,
    AggregatedProductResponse,
    RawProductFilters,
    RawProductResponse,
)
from app.schemas.entitlement import EntitlementResponse

router = APIRouter(prefix="/products")


@router.get("/aggregated")
async def get_aggregated_products(
    filters: Annotated[AggregatedProductFilters, Query()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Sequence[AggregatedProductResponse]:
    aggregated_products = await product_service.get_aggregated_products(
        session=session, filters=filters
    )

    return [AggregatedProductResponse.model_validate(ap) for ap in aggregated_products]


@router.get("/aggregated/{product_id}")
async def get_aggregated_product(
    product_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AggregatedProductResponse:
    aggregated_product = await product_service.get_aggregated_product(
        session=session, product_id=product_id
    )
    if not aggregated_product:
        raise HTTPException(404, detail="Aggregation product was not found.")

    return AggregatedProductResponse.model_validate(aggregated_product)


@router.post("/aggregated/{product_id}/purchase")
async def purchase_aggregated_product(
    product_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> EntitlementResponse:
    if not user.org_id:
        raise HTTPException(403, "User does not belong to an organization.")

    response = await product_service.purchase_aggregated_product(
        session=session, org_id=user.org_id, product_id=product_id
    )

    return EntitlementResponse.model_validate(response)


@router.get("/raw")
async def get_raw_products(
    filters: Annotated[RawProductFilters, Query()],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Sequence[RawProductResponse]:
    raw_products = await product_service.get_raw_products(
        session=session, filters=filters
    )

    return [RawProductResponse.model_validate(rp) for rp in raw_products]


@router.get("/raw/{product_id}")
async def get_raw_product(
    product_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RawProductResponse:
    raw_product = await product_service.get_raw_product(
        session=session, product_id=product_id
    )
    if not raw_product:
        raise HTTPException(404, detail="Raw product was not found.")

    return RawProductResponse.model_validate(raw_product)


@router.post("/raw/{product_id}/purchase")
async def purchase_raw_product(
    product_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> EntitlementResponse:
    if not user.org_id:
        raise HTTPException(403, "User does not belong to an organization.")
    response = await product_service.purchase_raw_product(
        session=session, org_id=user.org_id, product_id=product_id
    )

    return EntitlementResponse.model_validate(response)
