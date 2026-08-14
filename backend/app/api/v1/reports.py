from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_current_user, get_db
from app.models.core.user import User
from app.models.billing.entitlement import Entitlement

from app.services import report_service

from app.schemas.aggregated_report import AggregatedReportResponse
from app.schemas.raw_report import RawReportResponse
from app.schemas.report_list import ReportListResponse

router = APIRouter(prefix="/reports")


@router.get("")
async def get_reports(
    org_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportListResponse:
    if not user.org_id:
        raise HTTPException(403, detail="User does not belong to an organization.")
    reports = await report_service.get_reports(session=session, org_id=user.org_id)
    return ReportListResponse(total_count=len(reports), items=reports)


@router.get("/{entitlement_id}")
async def get_report_detail(
    entitlement_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Union[RawReportResponse, AggregatedReportResponse]:
    if not user.org_id:
        raise HTTPException(403, detail="User does not belong to an organization.")

    entitlement_query = select(Entitlement).where(
        Entitlement.entitlement_id == entitlement_id
    )
    entitlement_result = await session.execute(entitlement_query)
    entitlement = entitlement_result.scalar_one_or_none()

    if not entitlement:
        raise HTTPException(404, detail="Entitlement does not exist")

    if entitlement.raw_product_id:
        return await report_service.get_raw_report(
            session=session, entitlement_id=entitlement_id, org_id=user.org_id
        )
    elif entitlement.aggregated_product_id:
        # return await report_service.get_aggregated_report(
        #     session=session, entitlement_id=entitlement_id, org_id=user.org_id
        if True:  # TODO: placeholder unit the aggrregated reports are implemented
            raise HTTPException(
                status_code=501, detail="Aggregated reports are not implemented yet."
            )

    else:
        raise HTTPException(422, detail="Entitlement has no associated product.")
