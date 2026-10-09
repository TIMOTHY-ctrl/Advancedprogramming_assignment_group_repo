from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement
from src.application.Repositories.ITripAdvertisementRepository import ITripAdvertisementRepository


class InMemoryTripAdvertisementRepository(ITripAdvertisementRepository):
    def __init__(self) -> None:
        self._advertisements: dict[str, TripAdvertisement] = {}

    def put(self, advertisement: TripAdvertisement) -> None:
        self._advertisements[advertisement.trip_number] = advertisement

    def find_by_number(self, trip_number: str) -> TripAdvertisement | None:
        return self._advertisements.get(trip_number)

    def list_available(self) -> list[TripAdvertisement]:
        return [ad for ad in self._advertisements.values() if ad.active]
