from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.core.database import Base


class AggregationSource(Base):
    __tablename__ = "aggregation_sources"
    aggregation_id: Mapped[int] = mapped_column(
        ForeignKey("aggregations.aggregation_id"), primary_key=True
    )
    accommodation_data_id: Mapped[int | None] = mapped_column(
        ForeignKey("accommodation_data.accommodation_data_id"), nullable=True
    )
    external_data_id: Mapped[int | None] = mapped_column(
        ForeignKey("external_data.external_data_id"), nullable=True
    )
