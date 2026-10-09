from abc import ABC, abstractmethod
from src.Domain.Aggregate.TripAdvertisementAggregate.TripAdvertisement import TripAdvertisement


class ITripAdvertisementRepository(ABC):
    @abstractmethod
    def put(self, advertisement: TripAdvertisement) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_number(self, trip_number: str) -> TripAdvertisement | None:
        raise NotImplementedError

    @abstractmethod
    def list_available(self) -> list[TripAdvertisement]:
        raise NotImplementedError
