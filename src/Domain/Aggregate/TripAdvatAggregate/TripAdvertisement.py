from dataclasses import dataclass, replace
from datetime import datetime


@dataclass(frozen=True)
class TripAdvertisement:
    """Aggregate B, identified by trip_number; transitions return new state."""
    trip_number: str
    departure_time: datetime
    available_seats: int
    active: bool = True

    def __post_init__(self) -> None:
        if not self.trip_number.strip():
            raise ValueError('Trip number cannot be empty')
        if not isinstance(self.departure_time, datetime):
            raise ValueError('Departure time must be a datetime')
        if isinstance(self.available_seats, bool) or not isinstance(self.available_seats, int):
            raise ValueError('Available seats must be an integer')
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
            raise ValueError('advertisement already withdrawn')
        return replace(self, active=False, available_seats=0)
