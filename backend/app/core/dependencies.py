from typing import Annotated

from fastapi import Response, Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.core.organization import Organization
from app.models.core.user import User


security = HTTPBearer()


async def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    # Extract the token that comes in the Authorization Header
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            key=settings.clerk_jwks_public_key,
            algorithms=["RS256"],
        )

        return payload

    except jwt.exceptions.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )


async def get_current_user(
    payload=Depends(verify_token), session: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    query = select(User).where(User.external_id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


async def get_current_org(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
):
    org_id = user.org_id
    if org_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    query = select(Organization).where(Organization.org_id == org_id)

    result = await session.execute(query)

    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Organization not found"
        )

    return organization
