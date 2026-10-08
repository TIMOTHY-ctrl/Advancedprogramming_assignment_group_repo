from dataclasses import dataclass

from src.Domain.ValueObject.setnumber import SeatNumber


@dataclass(frozen=True)
class Booking:
    booking_id: str
    trip_number: str
    passenger_name: str
    seat_number: SeatNumber