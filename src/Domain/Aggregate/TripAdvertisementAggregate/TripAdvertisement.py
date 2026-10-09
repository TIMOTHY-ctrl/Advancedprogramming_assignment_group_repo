from dataclasses import dataclass, replace
from datetime import datetime


class AdvertisementAlreadyWithdrawn(ValueError):
    pass


@dataclass(frozen=True, eq=False)
class TripAdvertisement:
    """Aggregate B, identified by trip_number; transitions return new state."""
    trip_number: str
    departure_time: datetime
    available_seats: int
    active: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.trip_number, str) or not self.trip_number.strip():
            raise ValueError('Trip number cannot be empty')
        if not isinstance(self.departure_time, datetime):
            raise ValueError('Departure time must be a datetime')
        if isinstance(self.available_seats, bool) or not isinstance(self.available_seats, int):
            raise ValueError('Available seats must be an integer')
        if not isinstance(self.active, bool):
            raise ValueError('Advertisement active state must be boolean')
        if self.active and self.available_seats <= 0:
            raise ValueError('Active advertisements must have available seats')
        if not self.active and self.available_seats != 0:
            raise ValueError('Withdrawn advertisements must have zero available seats')

    def update_availability(self, available_seats: int) -> 'TripAdvertisement':
        if not self.active:
            raise ValueError('Cannot update a withdrawn advertisement')
        return replace(self, available_seats=available_seats)

    def withdraw(self) -> 'TripAdvertisement':
        # BR5 follow-up guard: withdrawal is a one-way transition.
        if not self.active:
            raise AdvertisementAlreadyWithdrawn('advertisement already withdrawn')
        return replace(self, active=False, available_seats=0)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TripAdvertisement) or type(other) is not type(self):
            return NotImplemented
        return self.trip_number == other.trip_number

    def __hash__(self) -> int:
        return hash((type(self), self.trip_number))
