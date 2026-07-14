from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.billing.entitlement import Entitlement


async def get_entitlements(
    session: AsyncSession,
    org_id: int,
    is_active: bool | None = None,
) -> Sequence[Entitlement]:
    query = select(Entitlement).where(Entitlement.org_id == org_id)
    if is_active is not None:
        query = query.where(Entitlement.is_active == is_active)
    result = await session.execute(query)
    return result.scalars().all()


async def get_entitlement(
    session: AsyncSession, entitlement_id: int, include_inactive: bool = False
) -> Entitlement | None:
    query = select(Entitlement).where(Entitlement.entitlement_id == entitlement_id)
    if not include_inactive:
        query = query.where(Entitlement.is_active)

    result = await session.execute(query)
    entitlement = result.scalar_one_or_none()

    return entitlement
