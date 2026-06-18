from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from svix.webhooks import Webhook, WebhookVerificationError
from clerk_backend_api import Clerk

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import verify_token
from app.schemas.auth import OnboardingRequest, OnboardingResponse
from app.services.organizations_service import create_organization
from app.services.user_service import create_user

router = APIRouter()


@router.post("/webhooks/clerk/user", status_code=status.HTTP_204_NO_CONTENT)
async def webhook_handler(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
):
    headers = request.headers
    payload = await request.body()
    try:
        wh = Webhook(settings.clerk_webhook_signing_secret)
        msg = wh.verify(payload, headers)
    except WebhookVerificationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    type = msg.get("type")
    if type == "user.created":
        return
    elif type == "user.updated":
        return
    elif type == "user.deleted":
        return


@router.post("/auth/onboarding")
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
