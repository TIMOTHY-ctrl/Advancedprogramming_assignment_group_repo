from contextlib import contextmanager
from collections.abc import Iterator
from datetime import datetime
from threading import RLock

from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Aggregate.TripAdvertisementAggregate.TripAdvertisement import TripAdvertisement


class InMemoryStore:
    """Shared process-local storage and transaction boundary.

    Roots are detached at repository boundaries, so shallow dictionary snapshots
    are sufficient. A reentrant lock supports handler calls inside a use case.
    This provides single-process atomicity, not distributed durability.
    """

    def __init__(self) -> None:
        self.lock = RLock()
        self.trips: dict[str, Trip] = {}
        self.advertisements: dict[str, TripAdvertisement] = {}
        self.departures: dict[tuple[str, datetime], str] = {}

    @contextmanager
    def transaction(self) -> Iterator[None]:
        with self.lock:
            snapshot = (self.trips.copy(), self.advertisements.copy(), self.departures.copy())
            try:
                yield
            except BaseException:
                self.trips, self.advertisements, self.departures = snapshot
                raise
