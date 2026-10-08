from abc import ABC, abstractmethod

from src.Domain.Aggregate.TripAggregate.trip import Trip


class ITripRepository(ABC):
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