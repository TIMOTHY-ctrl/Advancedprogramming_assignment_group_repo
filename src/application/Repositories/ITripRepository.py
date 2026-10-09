from abc import ABC, abstractmethod
from datetime import datetime

from src.Domain.Aggregate.TripAggregate.trip import Trip


class ITripRepository(ABC):
    """Reads are detached; changes become visible only after save.

    Implementations preserve identity and reject duplicate additions and unknown
    saves. Multi-operation workflows use the injected UnitOfWork.
    """

    @abstractmethod
    def find_departures(self, bus_number: str, departure_time: datetime) -> list[Trip]:
        raise NotImplementedError

    @abstractmethod
    def add(self, trip: Trip) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_number(self, trip_number: str) -> Trip | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Trip]:
        raise NotImplementedError

    @abstractmethod
    def save(self, trip: Trip) -> None:
        raise NotImplementedError
