import enum
from datetime import datetime

from sqlalchemy import func, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"


class Invitation(Base):
    __tablename__ = "invitations"

    invitation_id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.org_id"), nullable=False
    )
    email: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus), default=InvitationStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
