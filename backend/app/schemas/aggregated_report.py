from pydantic import BaseModel, Field
from typing import List


class ClusterInfo(BaseModel):
    name: str
    filter_type: str
    filter_value: str
    total_assets: int
    total_units: int
    est_total_revenue: float
    average_grade: str


class AggregatedFinancials(BaseModel):
    avg_revpar: float
    avg_adr: float
    est_gop_margin: float
    revpar_growth_percentage: float
    adr_growth_percentage: float


class MonthlySeasonality(BaseModel):
    month: str
    avg_occupancy: float
    avg_adr: float


class PerformanceDistribution(BaseModel):
    metric_name: str
    bottom_25_percent: float
    median: float
    top_25_percent: float


class SubSegment(BaseModel):
    name: str
    asset_count: int
    avg_revpar: float


class MarketSupply(BaseModel):
    new_assets_pipeline: int
    incoming_units: int
    avg_asset_age_years: float


class AggregateSatisfaction(BaseModel):
    guest_score_avg: float
    guest_score_top_performer: float
    employer_rating_avg: float


class ReportPeriod(BaseModel):
    year: int
    start: str
    end: str


class AggregatedReportResponse(BaseModel):
    period: ReportPeriod
    cluster: ClusterInfo
    financials: AggregatedFinancials
    seasonality: List[MonthlySeasonality] = Field(
        description="Cluster average seasonality curve."
    )
    distribution: List[PerformanceDistribution] = Field(
        description="Feeds the Box Plot chart showing market spread."
    )
    sub_segments: List[SubSegment] = Field(
        description="Dynamic internal breakdown of the cluster."
    )
    supply_risk: MarketSupply
    satisfaction: AggregateSatisfaction

    model_config = {
        "json_schema_extra": {
            "example": {
                "cluster": {
                    "name": "Canary Islands Market - Global",
                    "filter_type": "Geography",
                    "filter_value": "Canary Islands",
                    "total_assets": 45,
                    "total_units": 6520,
                    "est_total_revenue": 125000000.0,
                    "average_grade": "B+ (78/100)",
                },
                "financials": {
                    "avg_revpar": 112.0,
                    "avg_adr": 145.0,
                    "est_gop_margin": 32.0,
                    "revpar_growth_percentage": 5.0,
                    "adr_growth_percentage": 3.0,
                },
                "seasonality": [
                    {"month": "Jan", "avg_occupancy": 68.0, "avg_adr": 130.0}
                ],
                "distribution": [
                    {
                        "metric_name": "RevPAR",
                        "bottom_25_percent": 85.0,
                        "median": 105.0,
                        "top_25_percent": 140.0,
                    }
                ],
                "sub_segments": [
                    {"name": "Luxury (5 Stars)", "asset_count": 8, "avg_revpar": 160.0}
                ],
                "supply_risk": {
                    "new_assets_pipeline": 5,
                    "incoming_units": 850,
                    "avg_asset_age_years": 22.5,
                },
                "satisfaction": {
                    "guest_score_avg": 8.4,
                    "guest_score_top_performer": 9.6,
                    "employer_rating_avg": 3.5,
                },
            }
        }
    }
