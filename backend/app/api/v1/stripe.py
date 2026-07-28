from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from clerk_backend_api import Clerk

from app.core.config import settings
from app.models.core.user import User, UserRole
from app.core.dependencies import get_db, get_current_user
from app.core.dependencies import verify_token
from app.schemas.auth import OnboardingRequest, OnboardingResponse
from app.schemas.stripe_connect import StripeConnectStatus
from app.services.organizations_service import create_organization
from app.services.user_service import create_user

from app.services import stripe_service

router = APIRouter(prefix="/stripe")


@router.post("/connect/onboard")
async def create_connect_onboarding_url(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> str:
    if user.role != UserRole.org_admin:
        raise HTTPException(403, detail="Only org admins can connect.")

    if not user.org_id:
        raise HTTPException(403, detail="User does not belong to an organization.")

    url = await stripe_service.create_connect_onboarding_url(
        session=session, org_id=user.org_id
    )
    if not url:
        raise HTTPException(500, detail="Failed to create onboarding URL.")

    return url


@router.get("/connect/status")
async def get_connect_status(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> StripeConnectStatus:
    if not user.org_id:
        raise HTTPException(403, detail="User does not belong to an organization.")

    status = await stripe_service.get_connect_status(
        session=session, org_id=user.org_id
    )

    if not status:
        raise HTTPException(404, detail="Organization was not found.")

    return status
