from dataclasses import dataclass

from src.Domain.ValueObject.seatnumber import SeatNumber


@dataclass(frozen=True, eq=False)
class Booking:
    booking_id: str
    trip_number: str
    passenger_name: str
    seat_number: SeatNumber
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Booking) or type(other) is not type(self):
            return NotImplemented
        return self.booking_id == other.booking_id

    def __hash__(self) -> int:
        return hash((type(self), self.booking_id))
