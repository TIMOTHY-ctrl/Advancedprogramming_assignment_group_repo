from datetime import datetime
from src.Domain.Services.BusSchedulingPolicy import BusSchedulingPolicy

from src.Domain.Aggregate.TripAggregate.trip import Trip
from src.Domain.Entities.bus import Bus
from src.application.Repositories.ITripRepository import ITripRepository
from src.application.UseCases.UpdateAdvertisementService import (
    UpdateAdvertisementService,
)


class CreateTripService:
    def __init__(
        self,
        trip_repository: ITripRepository,
        advertisement_service: UpdateAdvertisementService,
        scheduling_policy: BusSchedulingPolicy | None = None,
    ) -> None:
        self._scheduling_policy = scheduling_policy or BusSchedulingPolicy()
        self._trip_repository = trip_repository
        self._advertisement_service = advertisement_service

    def execute(
        self, trip_number: str, departure_time: datetime, bus: Bus
    ) -> Trip:
        if self._trip_repository.find_by_number(trip_number) is not None:
            raise ValueError(f"Trip {trip_number} already exists")

        trip = Trip(trip_number, departure_time, bus)
        self._scheduling_policy.ensure_available(bus, departure_time, self._trip_repository.list_all())
        self._trip_repository.add(trip)
        self._advertisement_service.refresh(trip)
        return trip
