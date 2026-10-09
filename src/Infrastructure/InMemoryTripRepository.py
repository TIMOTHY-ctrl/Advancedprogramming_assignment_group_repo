from copy import deepcopy
from datetime import datetime

from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Infrastructure.InMemoryStore import InMemoryStore
from src.application.Repositories.ITripRepository import ITripRepository


class InMemoryTripRepository(ITripRepository):
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def add(self, trip: Trip) -> None:
        with self._store.lock:
            if trip.trip_number in self._store.trips:
                raise ValueError(f'Trip {trip.trip_number} already exists')
            key = (trip.bus.bus_number, trip.departure_time)
            if key in self._store.departures:
                raise ValueError('Bus is already scheduled at this departure time')
            self._store.trips[trip.trip_number] = deepcopy(trip)
            self._store.departures[key] = trip.trip_number

    def find_by_number(self, trip_number: str) -> Trip | None:
        with self._store.lock:
            return deepcopy(self._store.trips.get(trip_number))

    def find_departures(self, bus_number: str, departure_time: datetime) -> list[Trip]:
        with self._store.lock:
            number = self._store.departures.get((bus_number, departure_time))
            return [] if number is None else [deepcopy(self._store.trips[number])]

    def list_all(self) -> list[Trip]:
        with self._store.lock:
            return deepcopy(list(self._store.trips.values()))

    def save(self, trip: Trip) -> None:
        with self._store.lock:
            old = self._store.trips.get(trip.trip_number)
            if old is None:
                raise ValueError(f'Trip {trip.trip_number} does not exist')
            if old.departure_time != trip.departure_time or old.bus != trip.bus or old.capacity != trip.capacity:
                raise ValueError('A saved trip cannot change its scheduled bus or departure')
            self._store.trips[trip.trip_number] = deepcopy(trip)
