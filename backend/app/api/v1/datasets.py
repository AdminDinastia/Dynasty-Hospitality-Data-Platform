from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user, get_db
from app.schemas.dataset import DatasetResponse, DatasetUpdate
from app.models.core.user import User, UserRole
from app.services import dataset_service
from app.models.data.dataset import DatasetState


router = APIRouter(prefix="/datasets")


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    dataset = await dataset_service.get_dataset(session=session, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    if dataset.org_id != user.org_id:
        raise HTTPException(403, "Not authorized.")

    response = DatasetResponse.model_validate(dataset)

    return response


@router.get("")
async def get_datasets(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    accommodation_id: int | None = None,
    state: DatasetState | None = None,
):
    datasets = await dataset_service.get_datasets(
        session=session,
        org_id=user.org_id,
        accommodation_id=accommodation_id,
        state=state,
    )

    response = [DatasetResponse.model_validate(d) for d in datasets]

    return response


@router.patch("/{dataset_id}")
async def patch_dataset(
    data: DatasetUpdate,
    dataset_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    dataset = await dataset_service.get_dataset(
        session=session, dataset_id=dataset_id, include_inactive=True
    )

    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    if dataset.org_id != user.org_id:
        raise HTTPException(403, "Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(403, "Only org admins can update datasets.")

    updated_dataset = await dataset_service.update_dataset(
        session=session, data=data, dataset_id=dataset_id
    )

    return DatasetResponse.model_validate(updated_dataset)
