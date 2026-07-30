import enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum
from app.core.database import Base


class ChannelName(str, enum.Enum):
    direct_web = "direct_web"
    direct_phone = "direct_phone"
    booking_com = "booking_com"
    expedia = "expedia"
    hotels_com = "hotels_com"
    airbnb = "airbnb"
    hotelbeds = "hotelbeds"  # B2B wholesale leader in Spain
    tripadvisor = "tripadvisor"
    google_hotel = "google_hotel"
    lastminute = "lastminute"
    rumbo = "rumbo"  # Spanish OTA
    tui = "tui"  # German/UK tour operator, key in Canaries
    thomas_cook = "thomas_cook"  # UK tour operator
    jet2 = "jet2"  # UK market
    neckermann = "neckermann"  # German market
    kuoni = "kuoni"  # Swiss/UK market
    corendon = "corendon"  # Dutch/Belgian market
    sunweb = "sunweb"  # Dutch market
    loveholidays = "loveholidays"  # UK, growing
    on_the_beach = "on_the_beach"  # UK market
    corporate = "corporate"  # direct corporate contracts
    gds = "gds"  # Amadeus, Sabre, Galileo
    wholesale = "wholesale"  # generic wholesale
    other_ota = "other_ota"
    other_tour_operator = "other_tour_operator"
    other = "other"


class DistributionChannel(Base):
    __tablename__ = "distribution_channels"
    channel_id: Mapped[int] = mapped_column(primary_key=True)
    accommodation_id: Mapped[int] = mapped_column(
        ForeignKey("accommodations.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(nullable=False)
    channel_name: Mapped[ChannelName] = mapped_column(Enum(ChannelName), nullable=False)
    booking_percentage: Mapped[float] = mapped_column(nullable=False)
    commission_cost: Mapped[float | None] = mapped_column(nullable=True)
