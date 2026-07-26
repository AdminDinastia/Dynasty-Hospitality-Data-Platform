from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from app.models.core.organization import OrganizationType, Organization
from app.models.billing.points_ledger import PointsLedger, PointsReason
from app.core.config import WELCOME_POINTS


async def create_organization(
    session: AsyncSession,
    name: str,
    org_type: OrganizationType,
) -> Organization:
    new_organization = Organization(
        name=name, type=org_type, points_balance=WELCOME_POINTS
    )
    session.add(new_organization)
    try:
        await session.commit()
        new_ledger = PointsLedger(
            org_id=new_organization.org_id,
            points=WELCOME_POINTS,
            reason=PointsReason.welcome_bonus,
        )
        session.add(new_ledger)
        await session.commit()
        return new_organization
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Organization name already exists.")
