from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_db
from app.schemas.accommodation_data import (
    AccommodationDataResponse,
    AccommodationDataUpdate,
)
from app.models.core.user import User, UserRole
from app.services import accommodation_data_service
from app.models.data.accommodation_data import AccommodationDataState


router = APIRouter(prefix="/accommodation_data")


@router.get("/{accommodation_data_id}")
async def get_dataset(
    accommodation_data_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    dataset = await accommodation_data_service.get_dataset(
        session=session, accommodation_data_id=accommodation_data_id
    )
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    if dataset.org_id != user.org_id:
        raise HTTPException(403, "Not authorized.")

    response = AccommodationDataResponse.model_validate(dataset)

    return response


@router.get("")
async def get_datasets(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    accommodation_id: int | None = None,
    year: int | None = None,
    state: AccommodationDataState | None = None,
    include_historical: bool = False,
):
    datasets = await accommodation_data_service.get_datasets(
        session=session,
        org_id=user.org_id,
        year=year,
        include_historical=include_historical,
        accommodation_id=accommodation_id,
        state=state,
    )

    response = [AccommodationDataResponse.model_validate(d) for d in datasets]

    return response


@router.patch("/{accommodation_data_id}")
async def patch_dataset(
    data: AccommodationDataUpdate,
    accommodation_data_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    dataset = await accommodation_data_service.get_dataset(
        session=session,
        accommodation_data_id=accommodation_data_id,
        include_inactive=True,
    )

    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    if dataset.org_id != user.org_id:
        raise HTTPException(403, "Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(403, "Only org admins can update datasets.")

    updated_dataset = await accommodation_data_service.update_dataset(
        session=session, data=data, accommodation_data_id=accommodation_data_id
    )

    return AccommodationDataResponse.model_validate(updated_dataset)
