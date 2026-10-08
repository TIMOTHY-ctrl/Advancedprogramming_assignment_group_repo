from src.Domain.Aggregate.TripAdvatAggregate.TripAdvertisement import TripAdvertisement
from src.application.Repositories.ITripAdvertisementRepository import (
    ITripAdvertisementRepository,
)


class ListAvailableTripsService:
    def __init__(
        self, advertisement_repository: ITripAdvertisementRepository
    ) -> None:
        self._advertisement_repository = advertisement_repository

    def execute(self) -> list[TripAdvertisement]:
        return self._advertisement_repository.list_available()
