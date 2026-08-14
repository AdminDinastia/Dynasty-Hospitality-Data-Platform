from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.markeplace.product_status import ProductStatus


from app.models.accommodation.accommodation import CategorySystem, AccommodationType
from app.models.data.accommodation_data import GranularityType


class AggregatedProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    name: str
    description: str | None

    aggregation_id: int
    template_name: str

    price_points: int
    is_public: bool
    is_active: bool
    is_featured: bool
    status: ProductStatus
    created_at: datetime
    updated_at: datetime


class RawProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    name: str
    description: str | None
    year: int
    granularity: GranularityType
    accommodation_id: int
    template_name: str
    status: ProductStatus
    preview_config: dict | None
    price_points: int
    is_public: bool
    is_featured: bool
    is_active: bool


class AggregatedProductFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    country: str | None = None  # ES, FR (ISO 3166-1)
    nuts_code: str | None = None  # ES7, ES70, ES705 (level detected by lenght)
    city: str | None = None
    category_system: CategorySystem | None = None
    status: ProductStatus | None = None
    min_category: float | None = None
    max_category: float | None = None
    type: AccommodationType | None = None
    year_from: int | None = None
    year_to: int | None = None


class RawProductFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accommodation_id: int | None = None
    year: int | None = None
    status: ProductStatus | None = None
    granularity: GranularityType | None = None
    purchasable: bool | None = None
