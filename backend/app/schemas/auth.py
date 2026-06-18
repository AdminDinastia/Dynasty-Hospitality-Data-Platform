from pydantic import BaseModel

from app.models.core.organization import OrganizationType
from app.models.core.user import UserRole


class OnboardingRequest(BaseModel):
    org_name: str
    org_type: OrganizationType


class OnboardingResponse(BaseModel):
    user_id: int
    org_id: int
    org_name: str
    role: UserRole
