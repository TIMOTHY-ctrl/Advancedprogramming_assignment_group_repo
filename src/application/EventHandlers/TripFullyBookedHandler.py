from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.application.Repositories.ITripAdvertisementRepository import ITripAdvertisementRepository


class TripFullyBookedHandler:
    def __init__(self, advertisement_repository: ITripAdvertisementRepository) -> None:
        self._advertisement_repository = advertisement_repository

    def handle(self, event: TripFullyBooked) -> str:
        advertisement = self._advertisement_repository.find_by_number(event.trip_number)
        if advertisement is None:
            return 'rejected: advertisement does not exist'
        try:
            withdrawn = advertisement.withdraw()
        except ValueError as error:
            return f'rejected: {error}'
        self._advertisement_repository.put(withdrawn)
        return 'withdrawn'
