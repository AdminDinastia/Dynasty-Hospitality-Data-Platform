from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accommodation.data_sharing_consent import DataSharingConsent

from app.schemas.data_sharing import DataSharingUpdate

CURRENT_TERMS_VERSION = "1.0"


async def create_consent(
    session: AsyncSession, accommodation_id: int
) -> DataSharingConsent:
    new_consent = DataSharingConsent(
        accommodation_id=accommodation_id, terms_version=CURRENT_TERMS_VERSION
    )
    session.add(new_consent)
    await session.commit()
    return new_consent


async def update_consent(
    session: AsyncSession, accommodation_id: int, data: DataSharingUpdate
) -> DataSharingConsent | None:
    query = select(DataSharingConsent).where(
        DataSharingConsent.accommodation_id == accommodation_id
    )
    result = await session.execute(query)
    consent = result.scalar_one_or_none()

    if not consent:
        return None

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(consent, field, value)

    await session.commit()
    return consent
