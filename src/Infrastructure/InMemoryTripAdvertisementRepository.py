from src.Domain.Aggregate.TripAdvertisementAggregate.TripAdvertisement import TripAdvertisement
from src.application.Repositories.ITripAdvertisementRepository import ITripAdvertisementRepository
from src.Infrastructure.InMemoryStore import InMemoryStore


class InMemoryTripAdvertisementRepository(ITripAdvertisementRepository):
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def put(self, advertisement: TripAdvertisement) -> None:
        with self._store.lock:
            self._store.advertisements[advertisement.trip_number] = advertisement

    def find_by_number(self, trip_number: str) -> TripAdvertisement | None:
        with self._store.lock:
            return self._store.advertisements.get(trip_number)

    def list_available(self) -> list[TripAdvertisement]:
        with self._store.lock:
            return [ad for ad in self._store.advertisements.values() if ad.active]
