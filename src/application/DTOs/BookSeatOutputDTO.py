from dataclasses import dataclass


@dataclass(frozen=True)
class BookSeatOutputDTO:
    booking_id: str
    trip_number: str
    passenger_name: str
    seat_number: int
    available_seats: int
    advertisement_outcome: str
