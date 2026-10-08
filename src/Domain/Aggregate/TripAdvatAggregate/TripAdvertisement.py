from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TripAdvertisement:
    trip_number: str
    departure_time: datetime
    available_seats: int

    def __post_init__(self) -> None:
        if not self.trip_number.strip():
            raise ValueError("Trip number cannot be empty")
        if self.available_seats <= 0:
            raise ValueError("Only trips with available seats can be advertised")