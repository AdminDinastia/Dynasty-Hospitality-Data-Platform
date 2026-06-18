import enum

from sqlalchemy import func, Column, Integer, String, DateTime, ForeignKey, Enum

from app.core.database import Base


class InvitationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"


class Invitation(Base):
    __tablename__ = "invitations"

    invitation_id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.org_id"), nullable=False)
    email = Column(String, nullable=False)
    status = Column(
        Enum(InvitationStatus), default=InvitationStatus.pending, nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
