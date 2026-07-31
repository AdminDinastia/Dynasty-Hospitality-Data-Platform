from pydantic import BaseModel, Field
from typing import List, Optional

# --- 1. Core Sub-models ---


class InventoryUnit(BaseModel):
    unit_type: str
    count: int
    percentage: float


class Overview(BaseModel):
    total_units: int
    property_type: str
    asset_class: str
    rating_type: str
    rating_value: str
    grade: str
    year: int
    inventory_mix: List[InventoryUnit]


# --- 2. Financials Sub-models ---


class RevenueBreakdown(BaseModel):
    department: str
    revenue: float
    percentage: float


class YearlyPerformance(BaseModel):
    year: int
    occupancy: float
    adr: float
    revpar: float
    total_revenue: Optional[float] = None
    market_adr: Optional[float] = None


class MonthlyFinancials(BaseModel):
    month: str
    revenue: float
    revpar: float
    adr: float
    occupancy: float
    rooms_sold: int


class Financials(BaseModel):
    total_revenue: float
    revpar: float
    adr: float
    gop_margin: float

    revenue_breakdown: List[RevenueBreakdown] = Field(
        description="Used to render the Revenue Waterfall chart showing department contributions."
    )
    historical_performance: List[YearlyPerformance] = Field(
        description="Feeds the historical trendline chart (Area/Line chart) for Occupancy, ADR, and RevPAR."
    )
    forecast_next_year: YearlyPerformance = Field(
        description="Used for the forecast comparison table (Current Year vs Next Year)."
    )
    monthly_revenue: List[MonthlyFinancials] = Field(
        description="Used for the dual-axis combo chart (Total Revenue as bars, RevPAR/ADR as lines) and monthly occupancy bars."
    )


# --- 3. Operations Sub-models ---


class DayOfWeekOccupancy(BaseModel):
    day: str
    occupancy: float


class DistributionChannel(BaseModel):
    channel_name: str
    booking_percentage: float
    commission_cost: float


class Operations(BaseModel):
    average_occupancy: float
    lead_time_days: int
    length_of_stay: float
    cpor: float

    day_of_week_occupancy: List[DayOfWeekOccupancy] = Field(
        description="Feeds the Occupancy Heatmap (Days of the week vs. Occupancy density)."
    )
    distribution_channels: List[DistributionChannel] = Field(
        description="Used to render the Distribution Channel Treemap or segmented Donut chart."
    )


# --- 4. Market & Valuation Sub-models ---


class MarketComparison(BaseModel):
    metric: str
    hotel_value: float
    market_value: float
    differential: float


class Valuation(BaseModel):
    estimated_ebitda: float
    multiple_min: float
    multiple_max: float
    ev_min: float
    ev_max: float
    cap_rate: float
    payback_years_min: int
    payback_years_max: int


# --- 5. History & Risk Sub-models ---


class AssetEvent(BaseModel):
    date: str
    description: str


class AssetStatus(BaseModel):
    last_renovation_year: int
    building_age_years: int
    next_estimated_renovation: int
    certifications: List[str]


class LocalMarketRisk(BaseModel):
    pipeline_hotels: int
    incoming_capacity_rooms: int
    tourism_trend_percentage: float


class HistoryAndRisk(BaseModel):
    historical_events: List[AssetEvent] = Field(
        description="Iterated to render the Vertical Timeline UI component showing Capex and milestones."
    )
    asset_status: AssetStatus
    local_market: LocalMarketRisk


# --- 6. Satisfaction Sub-models ---


class TrendMetric(BaseModel):
    ltm_value: float
    historical_value: float
    differential: float


class QuarterlySatisfaction(BaseModel):
    quarter: str
    global_score: float
    staff_score: float
    cleanliness_score: float
    review_volume: int


class GuestSatisfaction(BaseModel):
    global_score: TrendMetric = Field(
        description="Renders the KPI card with a green/red directional trend arrow."
    )
    cleanliness_score: TrendMetric
    fb_score: TrendMetric
    quarterly_trend: List[QuarterlySatisfaction] = Field(
        description="Used for the combo chart showing score trendlines vs review volume background bars."
    )


class TeamHealth(BaseModel):
    employer_rating: TrendMetric = Field(
        description="Used for the Slope Chart connecting historical vs recent LTM scores."
    )
    management_approval: TrendMetric
    recommend_to_friend: TrendMetric


class SatisfactionAndTeam(BaseModel):
    guest_reviews: GuestSatisfaction
    employee_health: TeamHealth


# --- 7. Main Model (Full Report) ---


class RawReportResponse(BaseModel):
    property_name: str
    location: str
    overview: Overview
    financials: Financials
    operations: Operations

    market_positioning: List[MarketComparison] = Field(
        description="Used to render the Spider/Radar chart comparing the asset's silhouette against the market."
    )

    valuation: Valuation
    history_and_risk: HistoryAndRisk
    satisfaction: SatisfactionAndTeam

    # Swagger / OpenAPI Example Configuration
    model_config = {
        "json_schema_extra": {
            "example": {
                "property_name": "Hotel Santa Catalina",
                "location": "Las Palmas de Gran Canaria, ES705",
                "overview": {
                    "total_units": 202,
                    "property_type": "Hotel",
                    "asset_class": "Luxury",
                    "rating_type": "Stars",
                    "rating_value": "5",
                    "grade": "A+ (92/100)",
                    "year": 2024,
                    "inventory_mix": [
                        {
                            "unit_type": "Double Standard",
                            "count": 120,
                            "percentage": 59.4,
                        },
                        {
                            "unit_type": "Executive Suite",
                            "count": 32,
                            "percentage": 15.8,
                        },
                    ],
                },
                "financials": {
                    "total_revenue": 4250000.0,
                    "revpar": 145.0,
                    "adr": 185.0,
                    "gop_margin": 38.0,
                    "revenue_breakdown": [
                        {
                            "department": "Habitaciones",
                            "revenue": 2550000.0,
                            "percentage": 60.0,
                        },
                        {"department": "F&B", "revenue": 1062500.0, "percentage": 25.0},
                        {"department": "MICE", "revenue": 425000.0, "percentage": 10.0},
                        {
                            "department": "Spa y Otros",
                            "revenue": 212500.0,
                            "percentage": 5.0,
                        },
                    ],
                    "historical_performance": [
                        {
                            "year": 2021,
                            "occupancy": 52.0,
                            "adr": 155.0,
                            "revpar": 80.0,
                            "market_adr": 140.0,
                        },
                        {
                            "year": 2022,
                            "occupancy": 68.0,
                            "adr": 165.0,
                            "revpar": 112.0,
                            "market_adr": 150.0,
                        },
                        {
                            "year": 2023,
                            "occupancy": 75.5,
                            "adr": 176.0,
                            "revpar": 132.0,
                            "market_adr": 158.0,
                        },
                        {
                            "year": 2024,
                            "occupancy": 78.5,
                            "adr": 185.0,
                            "revpar": 145.0,
                            "market_adr": 162.0,
                        },
                    ],
                    "forecast_next_year": {
                        "year": 2025,
                        "occupancy": 80.2,
                        "adr": 192.0,
                        "revpar": 154.0,
                        "total_revenue": 4505000.0,
                    },
                    "monthly_revenue": [
                        {
                            "month": "Ene",
                            "revenue": 280000.0,
                            "revpar": 115.0,
                            "adr": 177.0,
                            "occupancy": 65.0,
                            "rooms_sold": 3953,
                        },
                        {
                            "month": "Feb",
                            "revenue": 310000.0,
                            "revpar": 127.0,
                            "adr": 177.0,
                            "occupancy": 72.0,
                            "rooms_sold": 4073,
                        },
                    ],
                },
                "operations": {
                    "average_occupancy": 78.5,
                    "lead_time_days": 45,
                    "length_of_stay": 4.2,
                    "cpor": 95.0,
                    "day_of_week_occupancy": [
                        {"day": "Monday", "occupancy": 65.0},
                        {"day": "Friday", "occupancy": 92.0},
                    ],
                    "distribution_channels": [
                        {
                            "channel_name": "Directo",
                            "booking_percentage": 35.0,
                            "commission_cost": 0.0,
                        },
                        {
                            "channel_name": "Booking.com",
                            "booking_percentage": 40.0,
                            "commission_cost": 18.0,
                        },
                        {
                            "channel_name": "Expedia",
                            "booking_percentage": 15.0,
                            "commission_cost": 20.0,
                        },
                    ],
                },
                "market_positioning": [
                    {
                        "metric": "Ocupacion",
                        "hotel_value": 78.5,
                        "market_value": 72.3,
                        "differential": 6.2,
                    },
                    {
                        "metric": "ADR",
                        "hotel_value": 185.0,
                        "market_value": 162.0,
                        "differential": 23.0,
                    },
                    {
                        "metric": "RevPAR",
                        "hotel_value": 145.0,
                        "market_value": 117.0,
                        "differential": 28.0,
                    },
                ],
                "valuation": {
                    "estimated_ebitda": 1615000.0,
                    "multiple_min": 10.0,
                    "multiple_max": 12.0,
                    "ev_min": 16100000.0,
                    "ev_max": 19300000.0,
                    "cap_rate": 7.0,
                    "payback_years_min": 9,
                    "payback_years_max": 11,
                },
                "history_and_risk": {
                    "historical_events": [
                        {
                            "date": "2022-03",
                            "description": "Renovacion completa habitaciones 150 hab. — 2.5M euros",
                        },
                        {
                            "date": "2023-06",
                            "description": "Upgrade categoria 4 stars a 5 stars",
                        },
                        {
                            "date": "2024-01",
                            "description": "Ampliacion 180 a 202 habitaciones",
                        },
                    ],
                    "asset_status": {
                        "last_renovation_year": 2022,
                        "building_age_years": 60,
                        "next_estimated_renovation": 2027,
                        "certifications": ["ISO 14001", "Bandera Azul"],
                    },
                    "local_market": {
                        "pipeline_hotels": 2,
                        "incoming_capacity_rooms": 450,
                        "tourism_trend_percentage": 8.0,
                    },
                },
                "satisfaction": {
                    "guest_reviews": {
                        "global_score": {
                            "ltm_value": 9.3,
                            "historical_value": 8.8,
                            "differential": 0.5,
                        },
                        "cleanliness_score": {
                            "ltm_value": 9.5,
                            "historical_value": 9.0,
                            "differential": 0.5,
                        },
                        "fb_score": {
                            "ltm_value": 8.9,
                            "historical_value": 9.1,
                            "differential": -0.2,
                        },
                        "quarterly_trend": [
                            {
                                "quarter": "Q1 2024",
                                "global_score": 9.5,
                                "staff_score": 9.6,
                                "cleanliness_score": 9.7,
                                "review_volume": 145,
                            },
                            {
                                "quarter": "Q4 2023",
                                "global_score": 9.2,
                                "staff_score": 9.4,
                                "cleanliness_score": 9.5,
                                "review_volume": 180,
                            },
                        ],
                    },
                    "employee_health": {
                        "employer_rating": {
                            "ltm_value": 4.3,
                            "historical_value": 3.6,
                            "differential": 0.7,
                        },
                        "management_approval": {
                            "ltm_value": 85.0,
                            "historical_value": 65.0,
                            "differential": 20.0,
                        },
                        "recommend_to_friend": {
                            "ltm_value": 80.0,
                            "historical_value": 55.0,
                            "differential": 25.0,
                        },
                    },
                },
            }
        }
    }
