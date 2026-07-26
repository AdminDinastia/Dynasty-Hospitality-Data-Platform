from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.core.user import UserRole, User


async def create_user(
    session: AsyncSession,
    external_id: str,
    org_id: int,
    email: str,
    role: UserRole = UserRole.org_admin,
):
    new_user = User(external_id=external_id, org_id=org_id, email=email, role=role)
    session.add(new_user)
    try:
        await session.commit()
        return new_user
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="User already exists.")


def update_user():
    pass


def delete_user():
    pass


def get_user_by_external_id(external_id: str):
    pass
