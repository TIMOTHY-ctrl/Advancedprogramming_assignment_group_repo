from collections.abc import Iterable
from datetime import datetime
from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Entities.bus import Bus


class BusSchedulingPolicy:
    """BR4: a bus may not serve two departures at the same instant.

    Duration and overlapping journeys are outside this small model's scope.
    The policy needs a proposed assignment and other trip aggregates.
    """

    def ensure_available(self, bus: Bus, departure_time: datetime,
                         existing_trips: Iterable[Trip]) -> None:
        if any(trip.bus.bus_number == bus.bus_number
               and trip.departure_time == departure_time
               for trip in existing_trips):
            raise ValueError('Bus is already scheduled at this departure time')
