from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import stripe

from app.models.billing.points_ledger import PointsLedger, PointsReason
from app.models.billing.payment_record import PaymentRecord, PaymentStatus
from app.models.core.organization import Organization
from app.core.config import settings
from app.core.config import POINTS_PER_EUR

stripe.api_key = settings.stripe_secret_key


async def get_balance(session: AsyncSession, org_id: int) -> int | None:
    query = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(query)
    org = result.scalar_one_or_none()

    if not org:
        return None

    return org.points_balance


async def get_history(session: AsyncSession, org_id: int) -> Sequence[PointsLedger]:
    query = select(PointsLedger).where(PointsLedger.org_id == org_id)
    result = await session.execute(query)
    points_ledgers = result.scalars().all()

    return points_ledgers


async def create_checkout_session(org_id: int, amount: float):
    points = int(amount * POINTS_PER_EUR)
    stripe_session = await stripe.checkout.Session.create_async(
        mode="payment",
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "unit_amount": int(amount * 100),
                    "product_data": {"name": f"{points} Plozeus Points"},
                },
                "quantity": 1,
            }
        ],
        metadata={
            "org_id": str(org_id),
            "points": str(points),
            "amount_eur": str(amount),
        },
        success_url=f"{settings.frontend_url}/purchase/success",
        cancel_url=f"{settings.frontend_url}/purchase/cancel",
    )
    return stripe_session.url


async def handle_payment_webhook(session: AsyncSession, event: stripe.Event):
    if event.type != "checkout.session.completed":
        return

    checkout_session = event.data.object
    org_id = int(checkout_session["metadata"]["org_id"])
    points = int(checkout_session["metadata"]["points"])
    amount = float(checkout_session["metadata"]["amount_eur"])

    query = select(Organization).where(Organization.org_id == org_id)
    result = await session.execute(query)
    org = result.scalar_one_or_none()
    if not org:
        return

    org.points_balance += int(points)

    new_leger = PointsLedger(org_id=org_id, points=points, reason=PointsReason.purchase)

    new_payment = PaymentRecord(
        org_id=org_id,
        amount=int(amount * 100),
        currency="EUR",
        points_awarded=points,
        stripe_payment_id=checkout_session.id,
        status=PaymentStatus.completed,
    )

    session.add(new_leger)
    session.add(new_payment)
    await session.commit()
    return
