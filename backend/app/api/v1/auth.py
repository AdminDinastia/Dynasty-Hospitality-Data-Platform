from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from clerk_backend_api import Clerk

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import verify_token
from app.schemas.auth import OnboardingRequest, OnboardingResponse
from app.services.organizations_service import create_organization
from app.services.user_service import create_user

router = APIRouter(prefix="/auth")


@router.post("/onboarding")
async def onboarding(
    data: OnboardingRequest,
    payload=Depends(verify_token),
    session: AsyncSession = Depends(get_db),
) -> OnboardingResponse:
    """creates organization + user"""
    external_id = payload.get("sub")
    async with Clerk(bearer_auth=settings.clerk_secret_key) as clerk:
        clerk_user = await clerk.users.get_async(user_id=external_id)
        email = clerk_user.email_addresses[0].email_address
        organization = await create_organization(
            session, data.org_name, org_type=data.org_type
        )
        user = await create_user(session, external_id, organization.org_id, email)
    return OnboardingResponse(
        user_id=user.user_id,
        org_id=organization.org_id,
        org_name=organization.name,
        role=user.role,
    )
