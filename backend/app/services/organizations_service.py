from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from app.models.core.organization import OrganizationType, Organization

WELCOME_POINTS = 1000


async def create_organization(
    session: AsyncSession,
    name: str,
    org_type: OrganizationType,
    points_balance: int = WELCOME_POINTS,
) -> Organization:
    new_organization = Organization(
        name=name, type=org_type, points_balance=points_balance
    )
    session.add(new_organization)
    try:
        await session.commit()
        return new_organization
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Organization name already exists.")
