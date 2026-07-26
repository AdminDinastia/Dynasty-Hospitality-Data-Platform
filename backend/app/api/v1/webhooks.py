from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from svix.webhooks import Webhook, WebhookVerificationError
import stripe
from app.core.config import settings

from app.core.database import get_db
from app.services import points_service

router = APIRouter(prefix="/webhooks")


@router.post("/clerk/user", status_code=status.HTTP_204_NO_CONTENT)
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


@router.post("/stripe/payment")
async def stripe_webhook(request: Request, session: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(400, detail="Invalid signature.")
    await points_service.handle_payment_webhook(session=session, event=event)
    return {"status": "ok"}
