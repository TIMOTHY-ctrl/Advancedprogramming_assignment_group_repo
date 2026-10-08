from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement
from src.application.Repositories.ITripAdvertisementRepository import (
    ITripAdvertisementRepository,
)


class InMemoryTripAdvertisementRepository(ITripAdvertisementRepository):
    def __init__(self) -> None:
        self._advertisements: dict[str, TripAdvertisement] = {}

    def put(self, advertisement: TripAdvertisement) -> None:
        self._advertisements[advertisement.trip_number] = advertisement

    def remove(self, trip_number: str) -> None:
        self._advertisements.pop(trip_number, None)

    def list_available(self) -> list[TripAdvertisement]:
        return list(self._advertisements.values())