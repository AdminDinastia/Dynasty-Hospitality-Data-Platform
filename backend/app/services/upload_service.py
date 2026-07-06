from typing import Sequence, Tuple


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.upload import UploadCreate
from app.models.data.upload import Upload, UploadStatus
from app.core.s3 import generate_presigned_url


async def create_upload(
    session: AsyncSession, data: UploadCreate, org_id: int
) -> Tuple[Upload, str]:
    new_upload = Upload(
        accommodation_id=data.accommodation_id,
        org_id=org_id,
        status=UploadStatus.pending,
        error_message=None,
        file_path="",
    )

    session.add(new_upload)
    await session.flush()

    presigned_url = generate_presigned_url(
        upload_id=new_upload.upload_id, org_id=org_id, filename=data.filename
    )

    new_upload.file_path = (
        f"bronze/org_id={org_id}/upload_id={new_upload.upload_id}/{data.filename}"
    )

    await session.commit()
    await session.refresh(new_upload)

    return new_upload, presigned_url


async def confirm_upload(session: AsyncSession, upload_id: int):
    query = select(Upload).where(Upload.upload_id == upload_id)
    result = await session.execute(query)
    upload = result.scalar_one_or_none()

    if not upload:
        return None

    upload.status = UploadStatus.processing

    await session.commit()
    await session.refresh(upload)
    return upload


async def get_uploads(
    session: AsyncSession,
    org_id: int,
    status: UploadStatus | None,
    accommodation_id: int | None,
) -> Sequence[Upload]:
    query = select(Upload).where(Upload.org_id == org_id).where(Upload.is_active)

    if status:
        query = query.where(Upload.status == status)

    if accommodation_id:
        query = query.where(Upload.accommodation_id == accommodation_id)

    result = await session.execute(query)
    uploads = result.scalars().all()
    return uploads


async def get_upload(session: AsyncSession, upload_id: int):
    query = select(Upload).where(Upload.upload_id == upload_id).where(Upload.is_active)
    result = await session.execute(query)
    upload = result.scalar_one_or_none()

    if not upload:
        return None

    return upload
