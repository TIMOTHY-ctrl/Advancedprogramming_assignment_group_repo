from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.application.Repositories.ITripAdvertisementRepository import (
    ITripAdvertisementRepository,
)


class TripFullyBookedHandler:
    def __init__(
        self, advertisement_repository: ITripAdvertisementRepository
    ) -> None:
        self._advertisement_repository = advertisement_repository

    def handle(self, event: TripFullyBooked) -> None:
        self._advertisement_repository.remove(event.trip_number)