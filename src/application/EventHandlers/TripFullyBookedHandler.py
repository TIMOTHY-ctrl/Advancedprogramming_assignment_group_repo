from src.Domain.Events.TripFullyBooked import TripFullyBooked
from src.Domain.Aggregate.TripAdvertisementAggregate.TripAdvertisement import AdvertisementAlreadyWithdrawn
from src.application.Repositories.ITripAdvertisementRepository import ITripAdvertisementRepository
from src.application.Ports.Workflow import UnitOfWork
from src.application.DTOs.AdvertisementOutcome import (
    AdvertisementOutcome, AdvertisementStatus, RejectionReason,
)


class TripFullyBookedHandler:
    def __init__(self, advertisement_repository: ITripAdvertisementRepository,
                 unit_of_work: UnitOfWork) -> None:
        self._advertisement_repository = advertisement_repository
        self._unit_of_work = unit_of_work

    def handle(self, event: TripFullyBooked) -> AdvertisementOutcome:
        with self._unit_of_work.transaction():
            advertisement = self._advertisement_repository.find_by_number(event.trip_number)
            if advertisement is None:
                return AdvertisementOutcome(AdvertisementStatus.REJECTED, RejectionReason.MISSING)
            try:
                withdrawn = advertisement.withdraw()
            except AdvertisementAlreadyWithdrawn:
                return AdvertisementOutcome(AdvertisementStatus.REJECTED, RejectionReason.ALREADY_WITHDRAWN)
            self._advertisement_repository.put(withdrawn)
            return AdvertisementOutcome(AdvertisementStatus.WITHDRAWN)
