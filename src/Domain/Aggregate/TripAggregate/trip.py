from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from types import MappingProxyType
from collections.abc import Mapping

from src.Domain.Aggregate.TripAggregate.booking import Booking
from src.Domain.Entities.bus import Bus
from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.Domain.ValueObject.seatnumber import SeatNumber


@dataclass(frozen=True)
class Trip:
    trip_number: str
    departure_time: datetime
    bus: Bus
    _booked_seats: dict[int, Booking] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.trip_number.strip():
            raise ValueError("Trip number cannot be empty")
        if not isinstance(self.departure_time, datetime):
            raise ValueError("Departure time must be a datetime")
        if not isinstance(self.bus, Bus):
            raise ValueError("Trip must be assigned a bus")

    @property
    def booked_seats(self) -> Mapping[int, Booking]:
        return MappingProxyType(self._booked_seats)

    @property
    def capacity(self) -> int:
        return self.bus.capacity

    @property
    def available_seats(self) -> int:
        return self.capacity - len(self._booked_seats)

    @property
    def has_available_seats(self) -> bool:
        return self.available_seats > 0

    def book_seat(
        self,
        passenger_name: str,
        seat_number: SeatNumber,
    ) -> tuple[Booking, TripFullyBooked | None]:
        if seat_number.value > self.capacity:
            raise ValueError(
                f"Seat number must be between 1 and {self.capacity}"
            )
        if not self.has_available_seats:
            raise ValueError("Trip is fully booked")
        if seat_number.value in self._booked_seats:
            raise ValueError("Seat is already booked")
        if not isinstance(passenger_name, str) or not passenger_name.strip():
            raise ValueError("Passenger name cannot be empty")

        booking = Booking(
            booking_id=uuid4().hex,
            trip_number=self.trip_number,
            passenger_name=passenger_name.strip(),
            seat_number=seat_number,
        )
        self._booked_seats[seat_number.value] = booking
        event = (
            TripFullyBooked(self.trip_number)
            if not self.has_available_seats
            else None
        )
        return booking, event
