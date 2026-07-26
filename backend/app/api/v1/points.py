from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.dependencies import get_db, get_current_user
from app.models.core.user import User
from app.services import points_service

from app.schemas.points import (
    PointsBalanceResponse,
    PointsHistoryResponse,
    PointsPurchaseRequest,
    PointsPurchaseResponse,
)

router = APIRouter(prefix="/points")


@router.get("/balance")
async def get_balance(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> PointsBalanceResponse:
    if not user.org_id:
        raise HTTPException(401, detail="User does not belong to an organization.")

    balance = await points_service.get_balance(org_id=user.org_id, session=session)

    if not balance:
        raise HTTPException(404, detail="User's organizations was not found.")

    return PointsBalanceResponse(org_id=user.org_id, points_balance=balance)


@router.get("/history")
async def get_history(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> Sequence[PointsHistoryResponse]:
    if not user.org_id:
        raise HTTPException(401, detail="User does not belong to an organization.")

    point_ledgers = await points_service.get_history(
        org_id=user.org_id, session=session
    )

    return [PointsHistoryResponse.model_validate(pl) for pl in point_ledgers]


@router.post("/purchase")
async def purchase(
    data: PointsPurchaseRequest, user: User = Depends(get_current_user)
) -> PointsPurchaseResponse:
    if not user.org_id:
        raise HTTPException(401, detail="User does not belong to an organization.")
    checkout_url = await points_service.create_checkout_session(
        org_id=user.org_id, amount=data.amount
    )
    return PointsPurchaseResponse(checkout_url=checkout_url)
