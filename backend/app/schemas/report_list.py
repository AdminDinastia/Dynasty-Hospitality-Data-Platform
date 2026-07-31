from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ReportListItem(BaseModel):
    entitlement_id: str
    report_type: str  # e.g., "raw" (individual) or "aggregated" (market cluster)
    title: str  # e.g., "Hotel Santa Catalina" or "Canary Islands Market"
    period_type: str  # e.g., "Yearly", "Quarterly", "Monthly"
    target_year: int  # e.g., 2024 (The year data belongs to)
    target_period: Optional[str] = None  # e.g., "Q1", "Full Year"
    created_at: datetime  # When the report was generated in the system
    status: str  # e.g., "completed", "processing"


class ReportListResponse(BaseModel):
    total_count: int
    items: List[ReportListItem] = Field(
        description="Paginated list of historical reports generated for the user or organization."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_count": 2,
                "items": [
                    {
                        "entitlement_id": "rep_9876",
                        "report_type": "raw",
                        "title": "Hotel Santa Catalina",
                        "period_type": "Yearly",
                        "target_year": 2024,
                        "target_period": "Full Year",
                        "created_at": "2026-06-01T10:30:00Z",
                        "status": "completed",
                    },
                    {
                        "entitlement_id": "rep_5432",
                        "report_type": "aggregated",
                        "title": "Canary Islands Market - 5 Stars",
                        "period_type": "Yearly",
                        "target_year": 2024,
                        "target_period": "Full Year",
                        "created_at": "2026-06-02T11:00:00Z",
                        "status": "completed",
                    },
                ],
            }
        }
    }
