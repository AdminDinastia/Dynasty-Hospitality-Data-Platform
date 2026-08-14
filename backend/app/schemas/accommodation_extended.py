from pydantic import BaseModel, ConfigDict

from app.models.accommodation.room_types import RoomCategory, RoomLevel
from app.models.accommodation.distribution_channels import ChannelName
from app.models.accommodation.revenue_breakdown import RevenueDepartment
from app.models.accommodation.accommodation_theme import ThemeType
from app.models.accommodation.accommodation_certification import CertificationType


class RoomTypeCreate(BaseModel):
    category: RoomCategory
    level: RoomLevel
    custom_name: str | None = None
    count: int


class RoomTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    room_type_id: int
    category: RoomCategory
    level: RoomLevel
    custom_name: str | None
    count: int
    percentage: float | None


class DistributionChannelCreate(BaseModel):
    year: int
    channel_name: ChannelName
    booking_percentage: float
    commission_cost: float | None = None


class DistributionChannelUpdate(BaseModel):
    booking_percentage: float | None = None
    commission_cost: float | None = None


class DistributionChannelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    channel_id: int
    accommodation_id: int
    year: int
    channel_name: ChannelName
    booking_percentage: float
    commission_cost: float | None


class RevenueBreakdownCreate(BaseModel):
    year: int
    department: RevenueDepartment
    revenue: float


class RevenueBreakdownResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    breakdown_id: int
    year: int
    department: RevenueDepartment
    revenue: float
    percentage: float | None


class AccommodationDetailsCreate(BaseModel):
    year: int
    lead_time_days: int | None = None
    length_of_stay: float | None = None
    cpor: float | None = None
    employee_count: int | None = None


class AccommodationDetailsUpdate(BaseModel):
    year: int | None = None
    lead_time_days: int | None = None
    length_of_stay: float | None = None
    cpor: float | None = None
    employee_count: int | None = None


class AccommodationDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    detail_id: int
    year: int | None
    lead_time_days: int | None
    length_of_stay: float | None
    cpor: float | None
    employee_count: int | None


class AccommodationThemeCreate(BaseModel):
    theme_type: ThemeType


class AccommodationThemeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    theme_id: int
    theme_type: ThemeType


class AccommodationCertificationCreate(BaseModel):
    certification_type: CertificationType
    custom_name: str | None = None
    obtained_year: int | None = None


class AccommodationCertificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    certification_id: int
    certification_type: CertificationType
    custom_name: str | None
    obtained_year: int | None
