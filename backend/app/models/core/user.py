from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy import func
from app.core.database import Base
import enum


class UserRole(enum.Enum):
    org_admin = "org_admin"
    org_member = "org_member"
    platform_admin = "platform_admin"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)

    # External auth provider user ID (Clerk/Auth0)
    external_id = Column(String)

    org_id = Column(Integer, ForeignKey("organizations.org_id"))
    email = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.org_member)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
