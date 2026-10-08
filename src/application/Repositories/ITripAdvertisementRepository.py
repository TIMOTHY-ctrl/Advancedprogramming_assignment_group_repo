from abc import ABC, abstractmethod

from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement


class ITripAdvertisementRepository(ABC):
    @abstractmethod
    def put(self, advertisement: TripAdvertisement) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, trip_number: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_available(self) -> list[TripAdvertisement]:
        raise NotImplementedError