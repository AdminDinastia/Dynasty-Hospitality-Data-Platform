from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data.upload import UploadStatus
from app.schemas.upload import UploadCreate, UploadCreateResponse, UploadResponse
from app.models.core.user import User, UserRole
from app.core.dependencies import get_current_user, get_db
from app.services import accommodation_service, upload_service


router = APIRouter(prefix="/uploads")


@router.post("")
async def create_upload(
    data: UploadCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UploadCreateResponse:
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can create accommodations."
        )
    accommodation = await accommodation_service.get_accommodation(
        session, data.accommodation_id
    )
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found.")
    if accommodation.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")

    upload, presigned_url = await upload_service.create_upload(
        session=session, data=data, org_id=accommodation.org_id
    )

    response = UploadCreateResponse(
        **UploadResponse.model_validate(upload).model_dump(),
        presigned_url=presigned_url,
    )

    return response


@router.post("/{upload_id}/confirm")
async def confirm_upload(
    upload_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UploadResponse:
    upload = await upload_service.get_upload(session=session, upload_id=upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found.")
    if upload.org_id != user.org_id:
        raise HTTPException(status_code=403, detail="Not authorized.")
    if user.role != UserRole.org_admin:
        raise HTTPException(
            status_code=403, detail="Only org admins can confirm uploads."
        )

    upload = await upload_service.confirm_upload(session=session, upload_id=upload_id)
    # TODO: trigger Dagster job
    return UploadResponse.model_validate(upload)


@router.get("")
async def get_uploads(
    status: UploadStatus | None = None,
    accommodation_id: int | None = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[UploadResponse]:
    uploads = await upload_service.get_uploads(
        session=session,
        org_id=user.org_id,
        status=status,
        accommodation_id=accommodation_id,
    )
    return [UploadResponse.model_validate(u) for u in uploads]


@router.get("/{upload_id}")
async def get_upload(
    upload_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    upload = await upload_service.get_upload(session=session, upload_id=upload_id)
    if not upload:
        raise HTTPException(404, "Upload not found.")
    # Check permissions
    if user.org_id != upload.org_id:
        raise HTTPException(403, "Not authorized.")
    return UploadResponse.model_validate(upload)
