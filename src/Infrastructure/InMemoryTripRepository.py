from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.application.Repositories.ITripRepository import ITripRepository


class InMemoryTripRepository(ITripRepository):
    def __init__(self) -> None:
        self._trips: dict[str, Trip] = {}

    def add(self, trip: Trip) -> None:
        if trip.trip_number in self._trips:
            raise ValueError(f"Trip {trip.trip_number} already exists")
        self._trips[trip.trip_number] = trip

    def find_by_number(self, trip_number: str) -> Trip | None:
        return self._trips.get(trip_number)

    def list_all(self) -> list[Trip]:
        return list(self._trips.values())

    def save(self, trip: Trip) -> None:
        if trip.trip_number not in self._trips:
            raise ValueError(f"Trip {trip.trip_number} does not exist")
        self._trips[trip.trip_number] = trip