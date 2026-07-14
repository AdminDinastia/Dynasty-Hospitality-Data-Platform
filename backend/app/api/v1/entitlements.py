from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.services import entitlement_service
from app.core.dependencies import get_current_user, get_db
from app.models.core.user import User
from app.schemas.entitlement import EntitlementResponse

router = APIRouter(prefix="/entitlements")


@router.get("")
async def get_entitlements(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> List[EntitlementResponse]:
    if not user.org_id:
        raise HTTPException(403, detail="User does not pertain to a organization.")

    entitlements = await entitlement_service.get_entitlements(
        session=session, org_id=user.org_id
    )

    response = [EntitlementResponse.model_validate(ent) for ent in entitlements]

    return response


@router.get("/{entitlement_id}")
async def get_entitlement(
    entitlement_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> EntitlementResponse:
    entitlement = await entitlement_service.get_entitlement(
        session=session, entitlement_id=entitlement_id
    )

    if not entitlement:
        raise HTTPException(404, detail="Entitlement not found.")

    if user.org_id != entitlement.org_id:
        raise HTTPException(
            403, detail="You do no that permissions to access this information."
        )

    return EntitlementResponse.model_validate(entitlement)
