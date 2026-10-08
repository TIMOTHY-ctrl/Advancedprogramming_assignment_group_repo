from dataclasses import dataclass


@dataclass(frozen=True)
class BookSeatInputDTO:
    trip_number: str
    passenger_name: str
    seat_number: int