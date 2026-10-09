from copy import deepcopy
from datetime import datetime
from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Infrastructure.InMemoryStore import InMemoryStore
from src.application.Repositories.ITripRepository import ITripRepository


class ReferenceTripRepository(ITripRepository):
    def __init__(self, store: InMemoryStore):
        self.store = store

    def find_by_number(self, trip_number: str) -> Trip | None:
        with self.store.lock:
            return deepcopy(self.store.trips.get(trip_number))

    def list_all(self) -> list[Trip]:
        with self.store.lock:
            return deepcopy(list(self.store.trips.values()))

    def find_departures(self, bus_number: str, departure_time: datetime) -> list[Trip]:
        return [trip for trip in self.list_all()
                if trip.bus.bus_number == bus_number and trip.departure_time == departure_time]

    def add(self, trip: Trip) -> None:
        with self.store.lock:
            if trip.trip_number in self.store.trips:
                raise ValueError('Trip already exists')
            if self.find_departures(trip.bus.bus_number, trip.departure_time):
                raise ValueError('Bus is already scheduled')
            self.store.trips[trip.trip_number] = deepcopy(trip)

    def save(self, trip: Trip) -> None:
        with self.store.lock:
            previous = self.store.trips.get(trip.trip_number)
            if previous is None:
                raise ValueError('Trip does not exist')
            if previous.departure_time != trip.departure_time or previous.bus != trip.bus or previous.capacity != trip.capacity:
                raise ValueError('A saved trip cannot change its scheduled bus or departure')
            self.store.trips[trip.trip_number] = deepcopy(trip)
