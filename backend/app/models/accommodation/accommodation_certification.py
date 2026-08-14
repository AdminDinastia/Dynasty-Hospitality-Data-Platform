import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum

from app.core.database import Base


class CertificationType(str, enum.Enum):
    iso_14001 = "iso_14001"
    iso_9001 = "iso_9001"
    travelife = "travelife"
    green_key = "green_key"
    blue_flag = "blue_flag"
    q_calidad_turistica = "q_calidad_turistica"
    breeam = "breeam"
    leed = "leed"
    other = "other"


class AccommodationCertification(Base):
    __tablename__ = "accommodation_certifications"
    certification_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )
    certification_type: Mapped[CertificationType] = mapped_column(
        Enum(CertificationType), nullable=False
    )
    custom_name: Mapped[str | None] = mapped_column(nullable=True)
    obtained_year: Mapped[int | None] = mapped_column(nullable=True)
