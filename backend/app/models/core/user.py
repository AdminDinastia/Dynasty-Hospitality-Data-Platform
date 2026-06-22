import enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(enum.Enum):
    org_admin = "org_admin"
    org_member = "org_member"
    platform_admin = "platform_admin"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)

    # External auth provider user ID (Clerk/Auth0)
    external_id: Mapped[str | None] = mapped_column(nullable=True)
    org_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=True
    )
    email: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.org_member
    )

    is_active: Mapped[bool] = mapped_column(
        default=True, nullable=False, server_default="true"
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
