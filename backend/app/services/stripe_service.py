from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import stripe

from app.models.core.user import User
from app.models.core.organization import Organization
from app.schemas.stripe_connect import StripeConnectStatus
from app.core.config import settings


async def create_connect_onboarding_url(
    session: AsyncSession, org_id: int
) -> str | None:
    query = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        return None

    account = await stripe.Account.create_async(type="express")

    organization.stripe_account_id = account.id
    await session.commit()

    account_link = await stripe.AccountLink.create_async(
        account=account.id,
        refresh_url=f"{settings.frontend_url}/stripe/reauth",
        return_url=f"{settings.frontend_url}/stripe/return",
        type="account_onboarding",
    )
    return account_link.url


async def get_connect_status(
    session: AsyncSession, org_id: int
) -> StripeConnectStatus | None:
    query = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(query)
    org = result.scalar_one_or_none()

    if not org:
        return None

    if org.stripe_account_id:
        account = await stripe.Account.retrieve_async(org.stripe_account_id)
        if account.charges_enabled:
            return StripeConnectStatus.connected
        else:
            return StripeConnectStatus.pending
    else:
        return StripeConnectStatus.not_connected
