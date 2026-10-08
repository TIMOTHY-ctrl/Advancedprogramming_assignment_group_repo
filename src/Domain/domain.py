from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Bus:
    bus_number: str
    capacity: int

    def __post_init__(self):
        if not isinstance(self.bus_number, str) or not self.bus_number.strip():
            raise ValueError("Bus number cannot be empty")
        if (
            isinstance(self.capacity, bool)
            or not isinstance(self.capacity, int)
            or self.capacity <= 0
        ):
            raise ValueError("Bus capacity must be a positive integer")


@dataclass
class Trip:
    trip_number: str
    departure_time: datetime
    bus: Bus
    booked_seats: set[int] = field(default_factory=set)

    @property
    def capacity(self) -> int:
        return self.bus.capacity

    @property
    def available_seats(self) -> int:
        return self.capacity - len(self.booked_seats)

    @property
    def has_available_seats(self) -> bool:
        return self.available_seats > 0

    def reserve_seat(self, seat_number: int) -> None:
        if isinstance(seat_number, bool) or not isinstance(seat_number, int):
            raise ValueError("Seat number must be an integer")
        if not 1 <= seat_number <= self.capacity:
            raise ValueError(f"Seat number must be between 1 and {self.capacity}")
        if not self.has_available_seats:
            raise ValueError("Trip is fully booked")
        if seat_number in self.booked_seats:
            raise ValueError("Seat is already booked")

        self.booked_seats.add(seat_number)


@dataclass(frozen=True)
class Booking:
    booking_id: int
    trip_number: str
    passenger_name: str
    seat_number: int


class BusBookingSystem:
    def __init__(self):
        self.trips: dict[str, Trip] = {}
        self.bookings: dict[int, Booking] = {}
        self._next_booking_id = 1

    def create_trip(
        self, trip_number: str, departure_time: datetime, bus: Bus
    ) -> Trip:
        if not isinstance(trip_number, str) or not trip_number.strip():
            raise ValueError("Trip number cannot be empty")
        if trip_number in self.trips:
            raise ValueError(f"Trip {trip_number} already exists")
        if not isinstance(departure_time, datetime):
            raise ValueError("Departure time must be a datetime")
        if not isinstance(bus, Bus):
            raise ValueError("Trip must be assigned a bus")

        trip = Trip(trip_number, departure_time, bus)
        self.trips[trip_number] = trip
        return trip

    def book_seat(
        self, trip_number: str, passenger_name: str, seat_number: int
    ) -> int:
        trip = self.get_trip(trip_number)
        if not isinstance(passenger_name, str) or not passenger_name.strip():
            raise ValueError("Passenger name cannot be empty")

        trip.reserve_seat(seat_number)
        booking_id = self._next_booking_id
        self._next_booking_id += 1
        self.bookings[booking_id] = Booking(
            booking_id, trip_number, passenger_name, seat_number
        )
        return booking_id

    def get_trip(self, trip_number: str) -> Trip:
        try:
            return self.trips[trip_number]
        except KeyError as error:
            raise ValueError(f"Trip {trip_number} does not exist") from error

    def get_available_trips(self) -> list[Trip]:
        return [trip for trip in self.trips.values() if trip.has_available_seats]

    def get_booking(self, booking_id: int) -> Booking:
        try:
            return self.bookings[booking_id]
        except KeyError as error:
            raise ValueError(f"Booking {booking_id} does not exist") from error
