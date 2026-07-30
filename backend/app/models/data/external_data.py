import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Enum, func

from app.core.database import Base


class ExternalDataSource(str, enum.Enum):
    eurostat = "eurostat"
    ine = "ine"
    scraping = "scraping"
    manual = "manual"


class ExternalData(Base):
    __tablename__ = "external_data"

    external_data_id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[ExternalDataSource] = mapped_column(
        Enum(ExternalDataSource), nullable=False
    )
    nuts_code: Mapped[str | None] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(nullable=False)
    storage_path: Mapped[str | None] = mapped_column(nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
